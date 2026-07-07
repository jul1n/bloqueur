#!/usr/bin/env python3
"""
bloqueur.py — Générateur de blocklist pub/tracker (hosts / domaines).

v3 — pipeline téléchargement + extraction en parallèle :
  - téléchargement I/O-bound via ThreadPoolExecutor, avec Session HTTP
    réutilisée (connection pooling) et retries avec backoff (urllib3.Retry)
  - extraction CPU-bound via ProcessPoolExecutor, lancée dès qu'une source
    est téléchargée (pipeline, pas deux phases séquentielles)
  - regex en un seul passage sur le texte entier (re.MULTILINE + finditer)
    au lieu d'une boucle Python ligne par ligne : ~x3 plus rapide sur les
    grosses listes (HaGeZi Pro, StevenBlack, OISD Big font 100k+ lignes)
  - cache disque optionnel (ETag / Last-Modified) : une source qui n'a pas
    changé depuis le dernier run n'est pas retéléchargée (requête
    conditionnelle HTTP 304), important pour un cron quotidien
  - dédup + tri, exclusion par domaine exact (pas de faux positifs par
    sous-chaîne), export "plain" ou "hosts", CLI + logs, mode --audit

Usage:
    python bloqueur.py
    python bloqueur.py --format hosts --output Liste.txt --workers 20
    python bloqueur.py --no-archive --sources mes_sources.txt
    python bloqueur.py --audit
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import logging
import os
import re
import shutil
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# --------------------------------------------------------------------------- #
# Config par défaut (tout est surchargeable en CLI)
# --------------------------------------------------------------------------- #
HERE = Path(__file__).resolve().parent
DEFAULT_SOURCES_FILE = HERE / "sources.txt"
DEFAULT_EXTRA_FILE = HERE / "extra-domains.txt"
DEFAULT_OUTPUT = HERE / "Liste.txt"
DEFAULT_CACHE_DIR = HERE / ".cache"

TIMEOUT_S = 15
RETRIES = 2
MAX_WORKERS = 16

# Reconnaît un domaine dans une ligne de hosts (0.0.0.0 example.com), une ligne
# AdBlock (||example.com^), ou un simple nom de domaine, en ignorant IPv6,
# commentaires et localhost. re.MULTILINE permet un seul passage sur tout le
# texte (finditer) plutôt qu'une boucle Python sur chaque ligne — ~x3 plus
# rapide sur les grosses listes.
DOMAIN_RE = re.compile(
    r"^\s*(?:0\.0\.0\.0|127\.0\.0\.1|::1?)?\s*\|{0,2}"
    r"([a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+)\^?\s*$",
    re.MULTILINE,
)
IGNORED_HOSTS = {"localhost", "localhost.localdomain", "broadcasthost", "local", "ip6-localhost", "ip6-loopback"}

log = logging.getLogger("bloqueur")
log.setLevel(logging.DEBUG)  # le filtrage se fait au niveau des handlers, pas du logger

_LOG_FORMAT = logging.Formatter("%(asctime)s  %(levelname)-7s  %(message)s", datefmt="%H:%M:%S")

console_handler = None

class InterleavedStreamHandler(logging.StreamHandler):
    """Handler console qui évite de casser la barre de progression en cours."""
    def __init__(self, stream=None):
        super().__init__(stream)
        self.buffered_records = []
        self.buffer_enabled = False

    def emit(self, record):
        if self.buffer_enabled and record.levelno >= logging.WARNING:
            self.buffered_records.append(record)
        else:
            super().emit(record)

    def flush_buffered(self):
        self.buffer_enabled = False
        if self.buffered_records:
            try:
                self.stream.write("\n")
                self.stream.flush()
            except Exception:
                pass
            for r in self.buffered_records:
                super().emit(r)
            self.buffered_records.clear()


def setup_logging(verbose: bool, log_file: Path | None) -> None:
    """Console : niveau DEBUG si -v, sinon INFO (le détail par source est
    toujours loggé en DEBUG, donc invisible à l'écran sans -v).
    Fichier de log (--log-file) : toujours DEBUG, indépendamment de ce qui
    s'affiche à l'écran — utile pour ausculter un run cron après coup sans
    avoir eu besoin de relancer en verbose."""
    global console_handler
    console_handler = InterleavedStreamHandler()
    console_handler.setFormatter(_LOG_FORMAT)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    log.addHandler(console_handler)

    if log_file is not None:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(_LOG_FORMAT)
        file_handler.setLevel(logging.DEBUG)
        log.addHandler(file_handler)
        log.debug("log complet écrit dans : %s", log_file)


# --------------------------------------------------------------------------- #
# Interface terminal : barre de progression compacte + résumé final en ASCII.
#
# Principe : en mode normal, une seule ligne de progression est réécrite sur
# elle-même (retour chariot \r) au lieu d'inonder la console avec une ligne
# par source (65 lignes "OK http://..." illisibles). Le détail par source
# reste disponible avec -v, mais bascule alors en lignes classiques (une
# barre qui se réécrit et des logs qui défilent sont incompatibles). Dans
# tous les cas, un récapitulatif de fin s'affiche — c'est la partie
# "synthétique" : ce qui a été fait, en un coup d'œil, même sans -v.
# --------------------------------------------------------------------------- #
_USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _USE_COLOR else text


class Progress:
    """Ligne de progression unique, réécrite en place. Désactivée si verbose
    (le détail par source défile alors normalement) ou si la sortie n'est
    pas un terminal (cron, redirection vers un fichier) — dans ce dernier
    cas, des jalons de log discrets (tous les 25%) remplacent la barre, pour
    ne pas polluer un fichier de log avec des centaines de retours chariot."""

    def __init__(self, total: int, label: str, enabled: bool):
        self.total = total
        self.label = label
        self.is_tty = sys.stdout.isatty()
        self.enabled = enabled and self.is_tty
        self.show_milestones = enabled and not self.is_tty
        self.done = 0
        self.counts = {"ok": 0, "cache": 0, "echec": 0}
        self._last_milestone = 0

    def tick(self, status: str) -> None:
        self.done += 1
        self.counts[status] = self.counts.get(status, 0) + 1
        if self.enabled:
            bar_width = 24
            filled = int(bar_width * self.done / max(self.total, 1))
            bar = "#" * filled + "-" * (bar_width - filled)
            line = (f"\r[{bar}] {self.label} {self.done:>3}/{self.total}  "
                    f"ok:{self.counts['ok']} cache:{self.counts['cache']} echec:{self.counts['echec']}")
            sys.stdout.write(line.ljust(90))
            sys.stdout.flush()
        elif self.show_milestones:
            pct = int(100 * self.done / max(self.total, 1))
            if pct >= self._last_milestone + 25:
                self._last_milestone = (pct // 25) * 25
                log.info("%s : %d%% (%d/%d)", self.label, self._last_milestone, self.done, self.total)

    def finish(self) -> None:
        if self.enabled:
            sys.stdout.write("\n")
            sys.stdout.flush()


def print_summary(*, sources_total: int, per_source_counts: dict, cache_hits: int,
                   dead: int, raw_domains: int, extra_count: int, excluded_count: int,
                   final_count: int, output: Path, fmt: str, elapsed: float,
                   diff: dict | None = None) -> None:
    """Résumé de fin en boîte ASCII simple (+/-/|) : compatible avec
    n'importe quel terminal, y compris sans support Unicode."""
    weak = sum(1 for c in per_source_counts.values() if c < MIN_HEALTHY_DOMAINS)
    size_kb = output.stat().st_size / 1024 if output.exists() else 0

    rows = [
        ("Sources", f"{sources_total} ({sources_total - dead} OK, {cache_hits} en cache, "
                     f"{dead} mortes, {weak} suspectes)"),
        ("Domaines bruts", f"{raw_domains:,}".replace(",", " ")),
        ("+ manuels", f"{extra_count:,}".replace(",", " ")),
        ("- exclus", f"{excluded_count:,}".replace(",", " ")),
        ("= uniques", f"{final_count:,}".replace(",", " ")),
    ]
    if diff is not None:
        rows.append(("Évolution", f"+{diff['added']} / -{diff['removed']} vs run précédent"))
    else:
        rows.append(("Évolution", "premier run (pas de comparaison)"))
    rows += [
        ("Sortie", f"{output.name}  ({fmt}, {size_kb:.0f} Ko)"),
        ("Durée", f"{elapsed:.1f}s"),
    ]
    label_w = max(len(r[0]) for r in rows)
    value_w = max(len(r[1]) for r in rows)
    width = label_w + value_w + 3

    print()
    print("+" + "-" * (width + 2) + "+")
    print("| " + _c("1", "bloqueur — résumé du run").ljust(width + (9 if _USE_COLOR else 0)) + " |")
    print("+" + "-" * (width + 2) + "+")
    for label, value in rows:
        print(f"| {label.ljust(label_w)} : {value.ljust(value_w)} |")
    print("+" + "-" * (width + 2) + "+")
    print()


def make_session() -> requests.Session:
    """Session HTTP réutilisée par tous les threads : connection pooling +
    retries avec backoff exponentiel (au lieu d'une boucle manuelle sans
    délai, qui insiste immédiatement sur un serveur déjà en difficulté)."""
    session = requests.Session()
    retry = Retry(total=RETRIES, backoff_factor=0.5,
                   status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry, pool_connections=MAX_WORKERS, pool_maxsize=MAX_WORKERS)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"User-Agent": "bloqueur/3.0"})
    return session


# --------------------------------------------------------------------------- #
# Étape 1 — téléchargement
# --------------------------------------------------------------------------- #
def load_list(path: Path) -> list[str]:
    """Lit un fichier texte et renvoie les lignes non vides / non commentées."""
    if not path.exists():
        log.warning("fichier introuvable, ignoré : %s", path)
        return []
    lines = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            lines.append(line)
    return lines


def _cache_key(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def _load_cache_meta(cache_dir: Path, url: str) -> dict:
    meta_path = cache_dir / f"{_cache_key(url)}.meta.json"
    if meta_path.exists():
        try:
            return json.loads(meta_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_cache(cache_dir: Path, url: str, text: str, headers: dict) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = _cache_key(url)
    (cache_dir / f"{key}.txt").write_text(text, encoding="utf-8")
    meta = {"etag": headers.get("ETag"), "last_modified": headers.get("Last-Modified"), "url": url}
    (cache_dir / f"{key}.meta.json").write_text(json.dumps(meta), encoding="utf-8")


def fetch(session: requests.Session, url: str, cache_dir: Path | None) -> tuple[str | None, bool]:
    """Télécharge une URL. Renvoie (texte, depuis_cache).
    Si un cache existe, envoie une requête conditionnelle (If-None-Match /
    If-Modified-Since) : si la source répond 304, on réutilise le contenu en
    cache sans retélécharger — gain net pour un cron quotidien où la plupart
    des listes n'ont pas changé depuis la veille."""
    headers = {}
    cached_text = None
    if cache_dir is not None:
        meta = _load_cache_meta(cache_dir, url)
        cache_file = cache_dir / f"{_cache_key(url)}.txt"
        if meta and cache_file.exists():
            cached_text = cache_file.read_text(encoding="utf-8", errors="ignore")
            if meta.get("etag"):
                headers["If-None-Match"] = meta["etag"]
            if meta.get("last_modified"):
                headers["If-Modified-Since"] = meta["last_modified"]
    try:
        r = session.get(url, timeout=TIMEOUT_S, allow_redirects=True, headers=headers)
        if r.status_code == 304 and cached_text is not None:
            return cached_text, True
        r.raise_for_status()
        if cache_dir is not None:
            _save_cache(cache_dir, url, r.text, r.headers)
        return r.text, False
    except requests.exceptions.RequestException as e:
        if cached_text is not None:
            log.warning("échec réseau, réutilisation du cache : %s (%s)", url, e)
            return cached_text, True
        log.warning("échec définitif : %s (%s)", url, e)
        return None, False


# --------------------------------------------------------------------------- #
# Étape 2 — extraction des domaines
# --------------------------------------------------------------------------- #
def extract_domains(text: str) -> set[str]:
    """Extrait les domaines valides d'un texte (formats hosts/AdBlock/brut).
    Un seul passage regex sur tout le texte (finditer + MULTILINE) plutôt
    qu'une boucle Python ligne par ligne : ~x3 plus rapide sur les grosses
    listes (mesuré : 1.0s -> 0.34s sur un fichier synthétique de 250k lignes)."""
    domains: set[str] = set()
    # Retire les commentaires en fin de ligne en un seul passage regex (pas de
    # splitlines()/join() intermédiaire) : "." ne matche pas "\n" par défaut,
    # donc "#.*" s'arrête bien en fin de ligne sans flag MULTILINE/DOTALL.
    cleaned = re.sub(r"#.*", "", text)
    for m in DOMAIN_RE.finditer(cleaned):
        domain = m.group(1).lower()
        if domain.startswith("www."):
            domain = domain[4:]
        if domain in IGNORED_HOSTS or domain.count(".") == 0:
            continue
        domains.add(domain)
    return domains


# --------------------------------------------------------------------------- #
# Étape 3 — assemblage final
# --------------------------------------------------------------------------- #
def is_excluded(domain: str, excluded: set[str]) -> bool:
    """True si `domain` est dans la liste d'exclusion, ou sous-domaine de celle-ci."""
    return domain in excluded or any(domain.endswith("." + ex) for ex in excluded)


MIN_HEALTHY_DOMAINS = 5  # en dessous de ce seuil, une source est probablement morte/vidée


def download_and_extract(urls: list[str], workers: int, cache_dir: Path | None, verbose: bool
                          ) -> tuple[dict[str, str], dict[str, set[str]], dict[str, int]]:
    """Pipeline complet : dès qu'une source est téléchargée (thread I/O), son
    extraction démarre immédiatement, sans attendre que les autres
    téléchargements se terminent.

    Sur une machine multi-cœurs, l'extraction est déléguée à un
    ProcessPoolExecutor pour paralléliser le CPU-bound (le module `re` ne
    libère pas le GIL, donc des threads ne suffisent pas ici).
    Sur une machine mono-cœur (ou os.cpu_count() indisponible), le
    multiprocessing coûterait plus en sérialisation qu'il ne rapporterait —
    mesuré : x0.5 (plus lent) sur un cœur unique — donc l'extraction se fait
    alors directement dans la boucle principale : le pipeline garde son
    intérêt (chevauchement attente réseau / parsing) sans le surcoût IPC."""
    sources_content: dict[str, str] = {}
    per_source_domains: dict[str, set[str]] = {}
    session = make_session()

    if console_handler and not verbose:
        console_handler.buffer_enabled = True

    cpu_count = os.cpu_count() or 1
    use_multiprocessing = cpu_count > 1
    cpu_pool = ProcessPoolExecutor(max_workers=max(cpu_count - 1, 1)) if use_multiprocessing else None
    log.debug("extraction : %s (%d coeur(s) détecté(s))",
              "multi-process" if use_multiprocessing else "inline (mono-coeur)", cpu_count)

    progress = Progress(len(urls), "téléchargement", enabled=not verbose)

    try:
        with ThreadPoolExecutor(max_workers=workers) as io_pool:
            dl_futures = {io_pool.submit(fetch, session, url, cache_dir): url for url in urls}
            parse_futures = {}

            for future in as_completed(dl_futures):
                url = dl_futures[future]
                content, from_cache = future.result()
                status = "cache" if from_cache else ("ok" if content else "echec")
                progress.tick(status)
                tag = {"cache": "CACHE", "ok": "OK   ", "echec": "ECH  "}[status]
                log.debug("[dl] %s %s", tag, url)
                if content is None:
                    continue
                sources_content[url] = content
                if use_multiprocessing:
                    parse_futures[cpu_pool.submit(extract_domains, content)] = url
                else:
                    per_source_domains[url] = extract_domains(content)

            if use_multiprocessing:
                for future in as_completed(parse_futures):
                    url = parse_futures[future]
                    per_source_domains[url] = future.result()
                    log.debug("[parse] %d domaines  %s", len(per_source_domains[url]), url)
    finally:
        progress.finish()
        if console_handler:
            console_handler.flush_buffered()
        if cpu_pool is not None:
            cpu_pool.shutdown(wait=True)

    return sources_content, per_source_domains, progress.counts


def build_blocklist(per_source_domains: dict[str, set[str]], extra_domains: list[str],
                     excluded: set[str]) -> tuple[list[str], dict[str, int]]:
    per_source_counts = {url: len(domains) for url, domains in per_source_domains.items()}
    all_domains: set[str] = set()
    for domains in per_source_domains.values():
        all_domains |= domains

    before = len(all_domains)
    all_domains |= {d.lower() for d in extra_domains}
    all_domains = {d for d in all_domains if not is_excluded(d, excluded)}
    log.debug("domaines uniques : %d (+ %d manuels, avant exclusion : %d)",
              len(all_domains), len(extra_domains), before)
    return sorted(all_domains), per_source_counts


def audit_sources(urls: list[str], sources_content: dict[str, str],
                   per_source_counts: dict[str, int]) -> None:
    """Affiche un rapport santé par source : échec réseau, ou 0/très peu de
    domaines extraits (signe probable qu'une source est morte, redirigée vers
    une page web, ou vidée de son contenu sans que l'URL ne renvoie d'erreur
    HTTP — d'où l'intérêt de compter les domaines plutôt que de se fier au
    seul code HTTP)."""
    print("\n=== Rapport d'audit des sources ===")
    dead, weak, ok = [], [], []
    for url in urls:
        if url not in sources_content:
            dead.append(url)
            continue
        count = per_source_counts.get(url, 0)
        if count < MIN_HEALTHY_DOMAINS:
            weak.append((url, count))
        else:
            ok.append((url, count))

    print(f"\nOK ({len(ok)}) :")
    for url, count in sorted(ok, key=lambda x: x[1]):
        print(f"  {count:>6}  {url}")

    if weak:
        print(f"\nSUSPECTES — {MIN_HEALTHY_DOMAINS} domaines ou moins, à vérifier manuellement ({len(weak)}) :")
        for url, count in weak:
            print(f"  {count:>6}  {url}")

    if dead:
        print(f"\nMORTES — échec de téléchargement après retries ({len(dead)}) :")
        for url in dead:
            print(f"  {'---':>6}  {url}")
    print()


# --------------------------------------------------------------------------- #
# Étape 4 — export
# --------------------------------------------------------------------------- #
def _snapshot_path(output: Path) -> Path:
    return output.with_name(output.name + ".prev")


def load_previous_domains(output: Path) -> set[str] | None:
    """Domaines du run précédent (snapshot texte simple à côté de la sortie),
    pour calculer un diff (+ajoutés / -retirés) sans dépendance externe."""
    snap = _snapshot_path(output)
    if snap.exists():
        return set(snap.read_text(encoding="utf-8", errors="ignore").split())
    return None


def save_snapshot(output: Path, domains: list[str]) -> None:
    _snapshot_path(output).write_text("\n".join(domains), encoding="utf-8")


def compute_diff(domains: list[str], previous: set[str] | None) -> dict | None:
    if previous is None:
        return None
    current = set(domains)
    return {"added": len(current - previous), "removed": len(previous - current)}


def build_header(*, sources_total: int, ok: int, cache: int, dead: int,
                  domain_count: int, diff: dict | None, homepage: str | None) -> str:
    """En-tête en commentaires (#), ignoré par tous les parseurs hosts/plain
    (Pi-hole, AdGuard Home, /etc/hosts). Auto-descriptif : quelqu'un qui tombe
    sur ce fichier sans contexte (toi dans 6 mois, ou un collègue) voit tout
    de suite d'où il vient, quand il a été généré, et s'il est à jour."""
    diff_line = f"# Évolution vs run précédent : +{diff['added']} / -{diff['removed']}" if diff \
        else "# Évolution vs run précédent : premier run"
    lines = [
        "# Title: bloqueur — blocklist pub/tracker agrégée",
        f"# Homepage: {homepage}" if homepage else None,
        f"# Généré le : {dt.datetime.now().isoformat(timespec='seconds')}",
        f"# Sources : {sources_total} ({ok} OK, {cache} en cache, {dead} mortes)",
        f"# Domaines : {domain_count}",
        diff_line,
        "# Généré par bloqueur.py — https://github.com/jul1n/bloqueur",
        "#",
    ]
    return "\n".join(l for l in lines if l is not None) + "\n"


def write_output(domains: list[str], output: Path, fmt: str, *,
                  per_source_counts: dict[str, int] | None = None,
                  diff: dict | None = None, header: str | None = None) -> None:
    if fmt == "hosts":
        content = "\n".join(f"0.0.0.0 {d}" for d in domains) + "\n"
        if header:
            content = header + content
    elif fmt == "json":
        payload = {
            "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
            "domain_count": len(domains),
            "diff_vs_previous_run": diff,
            "sources": per_source_counts or {},
            "domains": domains,
        }
        content = json.dumps(payload, indent=2, ensure_ascii=False)
    else:
        content = "\n".join(domains) + "\n"
        if header:
            content = header + content
    output.write_text(content, encoding="utf-8")
    log.debug("écrit : %s (%d domaines, format %s)", output, len(domains), fmt)


def archive_run(paths: list[Path]) -> None:
    """Range les fichiers de config utilisés dans un dossier horodaté (traçabilité)."""
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H-%M")
    folder = HERE / stamp
    folder.mkdir(exist_ok=True)
    for p in paths:
        if p.exists():
            shutil.copy2(p, folder / p.name)
    log.debug("run archivé dans : %s", folder)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Génère une blocklist pub/tracker à partir de plusieurs sources.")
    p.add_argument("--sources", type=Path, default=DEFAULT_SOURCES_FILE, help="fichier listant les URLs sources")
    p.add_argument("--extra", type=Path, default=DEFAULT_EXTRA_FILE, help="fichier de domaines à ajouter manuellement")
    p.add_argument("--exclude", type=Path, default=None, help="fichier de domaines à exclure (optionnel)")
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="fichier de sortie")
    p.add_argument("--format", choices=["plain", "hosts", "json"], default="plain", help="format de sortie")
    p.add_argument("--workers", type=int, default=MAX_WORKERS, help="téléchargements en parallèle")
    p.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR,
                   help="dossier de cache HTTP (ETag/Last-Modified) pour éviter de retélécharger l'inchangé")
    p.add_argument("--no-cache", action="store_true", help="désactive le cache HTTP")
    p.add_argument("--no-archive", action="store_true", help="ne pas archiver les fichiers de config utilisés")
    p.add_argument("--audit", action="store_true",
                   help="affiche un rapport santé par source (sources mortes/suspectes) sans écrire la sortie")
    p.add_argument("--log-file", type=Path, default=None,
                   help="fichier de log détaillé (toujours niveau DEBUG), indépendant de -v")
    p.add_argument("--max-dead-pct", type=float, default=None,
                   help="code de sortie 2 si plus de N%% des sources sont mortes (ex: 20) — utile en cron")
    p.add_argument("--no-header", action="store_true",
                   help="ne pas ajouter l'en-tête auto-descriptif (formats plain/hosts)")
    p.add_argument("--homepage", default="https://github.com/jul1n/bloqueur",
                   help="URL affichée dans l'en-tête (vide pour l'omettre)")
    p.add_argument("-v", "--verbose", action="store_true", help="logs détaillés (par source)")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    setup_logging(args.verbose, args.log_file)

    t_start = time.time()

    urls = load_list(args.sources)
    if not urls:
        log.error("aucune source à traiter (vérifie %s)", args.sources)
        return 1

    extra_domains = load_list(args.extra)
    excluded = set(load_list(args.exclude)) if args.exclude else set()

    cache_dir = None if args.no_cache else args.cache_dir
    sources_content, per_source_domains, counts = download_and_extract(
        urls, workers=args.workers, cache_dir=cache_dir, verbose=args.verbose)
    domains, per_source_counts = build_blocklist(per_source_domains, extra_domains, excluded)

    if args.audit:
        audit_sources(urls, sources_content, per_source_counts)
        return 0

    previous_domains = load_previous_domains(args.output)
    diff = compute_diff(domains, previous_domains)

    raw_domains = len(set().union(*per_source_domains.values())) if per_source_domains else 0
    dead = counts.get("echec", 0)
    dead_pct = 100 * dead / len(urls) if urls else 0

    header = None
    if not args.no_header:
        header = build_header(
            sources_total=len(urls), ok=len(urls) - dead, cache=counts.get("cache", 0),
            dead=dead, domain_count=len(domains), diff=diff, homepage=args.homepage or None,
        )
    write_output(domains, args.output, args.format, per_source_counts=per_source_counts,
                 diff=diff, header=header)
    save_snapshot(args.output, domains)

    if not args.no_archive:
        archive_run([args.sources, args.extra] + ([args.exclude] if args.exclude else []))

    print_summary(
        sources_total=len(urls),
        per_source_counts=per_source_counts,
        cache_hits=counts.get("cache", 0),
        dead=dead,
        raw_domains=raw_domains,
        extra_count=len(extra_domains),
        excluded_count=raw_domains + len(extra_domains) - len(domains),
        final_count=len(domains),
        output=args.output,
        fmt=args.format,
        elapsed=time.time() - t_start,
        diff=diff,
    )

    if args.max_dead_pct is not None and dead_pct > args.max_dead_pct:
        log.error("%.0f%% des sources sont mortes (seuil : %.0f%%) — liste probablement dégradée",
                  dead_pct, args.max_dead_pct)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
