# bloqueur

Génère une blocklist de domaines publicitaires/tracker à partir de ~60 sources
publiques (Firebog, StevenBlack, AdAway, PolishFiltersTeam, etc.), avec dédup,
nettoyage et export au format de ton choix.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python bloqueur.py
```

Options utiles :

| Option | Effet |
|---|---|
| `--format hosts` | export au format `0.0.0.0 domaine.com` (Pi-hole, AdGuard, /etc/hosts) |
| `--format plain` | un domaine par ligne (défaut) |
| `--format json` | JSON avec métadonnées (voir section dédiée ci-dessous) |
| `--output chemin.txt` | fichier de sortie (défaut `Liste.txt`) |
| `--sources fichier.txt` | fichier de sources alternatif |
| `--exclude fichier.txt` | domaines à exclure (protéger des faux positifs) |
| `--workers N` | téléchargements en parallèle (défaut 16) |
| `--cache-dir chemin` | dossier de cache HTTP (défaut `.cache`) |
| `--no-cache` | désactive le cache HTTP (retélécharge tout à chaque run) |
| `--no-archive` | ne pas archiver les fichiers de config utilisés |
| `--audit` | rapport santé par source (OK / suspecte / morte), n'écrit pas la sortie |
| `--log-file chemin.log` | log détaillé complet (toujours DEBUG), indépendant de ce qui s'affiche à l'écran |
| `--max-dead-pct N` | code de sortie 2 si plus de N% des sources sont mortes (utile en cron/monitoring) |
| `--no-header` | ne pas ajouter l'en-tête auto-descriptif (formats plain/hosts) |
| `--homepage URL` | URL affichée dans l'en-tête (vide pour l'omettre) |
| `-v` | logs détaillés à l'écran (par source) |

## Format JSON + suivi d'évolution

```bash
python bloqueur.py --format json --output Liste.json
```

Produit un JSON avec métadonnées :

```json
{
  "generated_at": "2026-07-07T19:51:09",
  "domain_count": 796210,
  "diff_vs_previous_run": {"added": 340, "removed": 12},
  "sources": {"https://...": 45123, "...": ...},
  "domains": ["ads1.example.com", "..."]
}
```

Un snapshot (`<sortie>.prev`) est conservé à côté du fichier de sortie pour
calculer `diff_vs_previous_run` au run suivant, quel que soit le format
choisi (plain/hosts/json) — le diff apparaît aussi dans le résumé ASCII
("Évolution : +340 / -12 vs run précédent"). Pratique pour surveiller une
dérive brutale (ex : une grosse liste qui se vide d'un coup après un run).

## Monitoring en cron

```bash
python bloqueur.py --log-file /var/log/bloqueur.log --max-dead-pct 20
```

- Le log complet (niveau détail `-v`) va dans le fichier, même sans `-v` à
  l'écran — l'écran reste synthétique (barre + résumé), le fichier garde
  tout pour investigation a posteriori.
- Si plus de 20% des sources sont mortes sur ce run, le script sort avec le
  code 2 (0 = ok, 1 = erreur de configuration, 2 = liste dégradée) — à
  brancher sur une alerte cron classique (`|| mail -s "bloqueur dégradé" ...`).

## Pipeline téléchargement + extraction

Avant : téléchargement parallèle, PUIS extraction séquentielle une fois tout
téléchargé (deux phases strictes).

Maintenant : dès qu'une source est téléchargée, son extraction démarre
immédiatement, en parallèle des téléchargements encore en cours.

- **Téléchargement** : `ThreadPoolExecutor`, session HTTP partagée
  (connection pooling) + retries avec backoff exponentiel (`urllib3.Retry`)
  au lieu d'une boucle manuelle qui réessaie sans délai.
- **Extraction** : le module `re` ne libère pas le GIL, donc des threads ne
  suffisent pas à paralléliser le CPU-bound. Sur une machine multi-cœurs,
  l'extraction est déléguée à un `ProcessPoolExecutor`. Sur mono-cœur (mesuré
  en conditions réelles), le multiprocessing coûte plus cher en sérialisation
  qu'il ne rapporte (x0.5, donc plus lent) — le script détecte
  `os.cpu_count()` et bascule automatiquement en extraction "inline" dans ce
  cas, tout en gardant l'avantage du pipeline (recouvrement attente réseau /
  CPU).
- **Regex optimisée** : un seul passage `finditer` + `re.MULTILINE` sur le
  texte entier au lieu d'une boucle Python ligne par ligne — mesuré x3 plus
  rapide sur un fichier synthétique de 250 000 lignes.
- **Cache HTTP conditionnel** (ETag / Last-Modified) : une source inchangée
  depuis le dernier run répond 304 et n'est pas retéléchargée. Utile pour un
  cron quotidien où la plupart des ~65 sources ne changent pas d'un jour à
  l'autre. Vérifié avec un serveur HTTP local : la 2ᵉ exécution affiche
  `CACHE` au lieu de `OK` pour les sources inchangées.

## Fichiers de configuration

- `sources.txt` — une URL de blocklist par ligne. Ajouter/retirer une source
  ne demande aucune modification du script.
- `extra-domains.txt` — domaines à toujours inclure (ta liste perso).
- un fichier d'exclusion optionnel (`--exclude`) pour protéger des domaines
  que les listes sources bloquent à tort.

## Interface terminal

- **Mode normal** : une barre de progression compacte, réécrite en place
  (`\r`), pas un flot de 65 lignes par source.
- **Mode `-v`** : détail complet par source (téléchargé/cache/échec, nombre
  de domaines extraits), en lignes classiques.
- **Sortie non-interactive** (cron, redirection vers un fichier) : la barre
  est automatiquement remplacée par des jalons de log à 25/50/75/100%, pour
  ne pas polluer un fichier de log avec des centaines de retours chariot.
- **Dans tous les cas**, un résumé de fin en boîte ASCII (`+`/`-`/`|`,
  compatible avec n'importe quel terminal) : sources OK/cache/mortes/
  suspectes, domaines bruts → uniques, fichier de sortie, durée.

```
+--------------------------------------------------------------+
| bloqueur — résumé du run                                     |
+--------------------------------------------------------------+
| Sources        : 65 (61 OK, 40 en cache, 4 mortes, 2 suspectes) |
| Domaines bruts : 812 345                                     |
| + manuels      : 174                                         |
| - exclus       : 12                                          |
| = uniques      : 796 210                                     |
| Sortie         : Liste.txt  (plain, 7421 Ko)                 |
| Durée          : 18.4s                                       |
+--------------------------------------------------------------+
```

## En-tête auto-descriptif

Les formats `plain` et `hosts` incluent par défaut un en-tête en commentaires
(`#`, ignoré par tous les parseurs hosts/Pi-hole/AdGuard) :

```
# Title: bloqueur — blocklist pub/tracker agrégée
# Homepage: https://github.com/jul1n/bloqueur
# Généré le : 2026-07-07T20:29:36
# Sources : 65 (61 OK, 40 en cache, 4 mortes)
# Domaines : 796210
# Évolution vs run précédent : +340 / -12
# Généré par bloqueur.py — https://github.com/jul1n/bloqueur
```

Utile si le fichier circule sans contexte (toi dans 6 mois, un collègue, un
autre outil qui l'importe) : on voit d'un coup d'œil d'où il vient et s'il
est à jour. Désactivable avec `--no-header`, URL personnalisable avec
`--homepage`.

## Publier automatiquement sur GitHub

Un workflow GitHub Actions (`.github/workflows/update-blocklist.yml`) génère
et committe `Liste.txt` chaque jour à 4h UTC (`workflow_dispatch` permet
aussi un déclenchement manuel depuis l'onglet Actions) :

- Le cache HTTP (`.cache/`) et le snapshot de diff (`Liste.txt.prev`) sont
  conservés entre les runs via `actions/cache`, donc le diff "+X/-Y vs run
  précédent" reste cohérent d'un jour à l'autre, et les sources inchangées
  ne sont pas retéléchargées.
- Si `--max-dead-pct 30` est dépassé, le job échoue et le log complet est
  publié comme artefact GitHub — visible dans l'onglet Actions sans avoir à
  aller chercher ailleurs.
- Rien n'est committé si la liste n'a pas changé (`git diff --cached
  --quiet`), pour éviter de polluer l'historique avec des commits vides.

Une fois en place, il suffit de pointer AdGuard Home vers l'URL brute :

```
https://raw.githubusercontent.com/jul1n/bloqueur/main/Liste.txt
```

exactement comme pour HaGeZi ou OISD — plus besoin de relancer le script à
la main sur chaque appareil.

## Ce qui a changé par rapport à `script_v1.1.4.py`

- Pipeline téléchargement + extraction en parallèle (voir section dédiée
  ci-dessus), au lieu de deux phases séquentielles.
- Cache HTTP conditionnel (ETag/Last-Modified) pour ne pas retélécharger
  l'inchangé.
- Regex en un seul passage (`finditer` + `MULTILINE`) au lieu d'une boucle
  Python ligne par ligne — ~x3 plus rapide.
- Extraction des domaines par regex générique (hosts, AdBlock, texte brut) au
  lieu de `.replace()` en chaîne — plus robuste, permet de réactiver des
  sources qui nécessitaient un post-traitement manuel.
- Traitement 100% en mémoire : plus de ~90 fichiers intermédiaires sur disque.
- Exclusion par domaine exact (et sous-domaines), plus de faux positifs par
  sous-chaîne (`163.com` ne supprime plus `1163.com`).
- Sources et domaines manuels dans des fichiers texte séparés, éditables sans
  toucher au code.
- Mode `--audit` pour repérer les sources mortes ou dégradées.
- Interface terminal : barre de progression compacte + résumé de fin en
  ASCII, détail complet réservé au mode `-v`.
- Format `json` avec métadonnées et diff vs le run précédent.
- `--log-file` : log complet indépendant de l'affichage écran.
- `--max-dead-pct` : code de sortie non-zéro si trop de sources mortes.
- En-tête auto-descriptif dans le fichier généré (titre, date, stats, diff).
- Workflow GitHub Actions pour générer et publier `Liste.txt` automatiquement.
- CLI (`argparse`) + logs structurés au lieu de `print()`.
