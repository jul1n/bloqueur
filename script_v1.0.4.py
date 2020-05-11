#charger la librairie python nécessaire
import urllib.request
import time, datetime, os, shutil

#définir les adresses des listes à importer
url01 = 'https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts'
url02 = 'https://mirror1.malwaredomains.com/files/justdomains'
url03 = 'http://sysctl.org/cameleon/hosts'
url04 = 'https://s3.amazonaws.com/lists.disconnect.me/simple_tracking.txt'
url05 = 'https://s3.amazonaws.com/lists.disconnect.me/simple_ad.txt'
url06 = 'https://raw.githubusercontent.com/Spam404/lists/master/main-blacklist.txt'
url07 = 'https://raw.githubusercontent.com/PolishFiltersTeam/KADhosts/master/KADhosts_without_controversies.txt'
url08 = 'https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.Spam/hosts'
url09 = 'https://v.firebog.net/hosts/static/w3kbl.txt'
url10 = 'https://adaway.org/hosts.txt'
url11 = 'https://v.firebog.net/hosts/AdguardDNS.txt'
url12 = 'https://raw.githubusercontent.com/anudeepND/blacklist/master/adservers.txt'
url13 = 'https://v.firebog.net/hosts/Easylist.txt'
url14 = 'https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=0&mimetype=plaintext'
url15 = 'https://raw.githubusercontent.com/FadeMind/hosts.extras/master/UncheckyAds/hosts'
url16 = 'https://raw.githubusercontent.com/bigdargon/hostsVN/master/hosts'
url17 = 'https://v.firebog.net/hosts/Easyprivacy.txt'
url18 = 'https://v.firebog.net/hosts/Prigent-Ads.txt'	
url19 = 'https://zerodot1.gitlab.io/CoinBlockerLists/hosts_browser'
url20 = 'https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.2o7Net/hosts' 	
url21 = 'https://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/hosts/spy.txt'
url22 = 'https://www.github.developerdan.com/hosts/lists/ads-and-tracking-extended.txt'
url23 = 'https://hostfiles.frogeye.fr/firstparty-trackers-hosts.txt'
url24 = 'https://raw.githubusercontent.com/DandelionSprout/adfilt/master/Alternate%20versions%20Anti-Malware%20List/AntiMalwareHosts.txt'
url25 = 'https://osint.digitalside.it/Threat-Intel/lists/latestdomains.txt'
url26 = 'https://s3.amazonaws.com/lists.disconnect.me/simple_malvertising.txt'
url27 = 'https://v.firebog.net/hosts/Prigent-Malware.txt'
url28 = 'https://mirror.cedia.org.ec/malwaredomains/immortal_domains.txt'
url29 = 'https://www.malwaredomainlist.com/hostslist/hosts.txt'
url30 = 'https://bitbucket.org/ethanr/dns-blacklists/raw/8575c9f96e5b4a1308f2f12394abd86d0927a4a0/bad_lists/Mandiant_APT1_Report_Appendix_D.txt'
url31 = 'https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.Risk/hosts'
url32 = 'https://urlhaus.abuse.ch/downloads/hostfile/'
url33 = 'https://v.firebog.net/hosts/Shalla-mal.txt'


#Ces listes posent problème
#urlXX = 'https://gitlab.com/quidsup/notrack-blocklists/raw/master/notrack-blocklist.txt'
#urlXX = 'https://phishing.army/download/phishing_army_blocklist_extended.txt'
#urlXX = 'https://gitlab.com/quidsup/notrack-blocklists/raw/master/notrack-malware.txt'
#urlXX = 'https://hosts-file.net/ad_servers.txt'

# Télécharge le fichier depuis `url` et l'enregristre localement suivant l'argument après la virgule
urllib.request.urlretrieve(url01, "Liste n°01.txt")
urllib.request.urlretrieve(url02, "Liste n°02.txt")
urllib.request.urlretrieve(url03, "Liste n°03.txt")
urllib.request.urlretrieve(url04, "Liste n°04.txt")
urllib.request.urlretrieve(url05, "Liste n°05.txt")
urllib.request.urlretrieve(url06, "Liste n°06.txt")
urllib.request.urlretrieve(url07, "Liste n°07.txt")
urllib.request.urlretrieve(url08, "Liste n°08.txt")
urllib.request.urlretrieve(url09, "Liste n°09.txt")
urllib.request.urlretrieve(url10, "Liste n°10.txt")
urllib.request.urlretrieve(url11, "Liste n°11.txt")
urllib.request.urlretrieve(url12, "Liste n°12.txt")
urllib.request.urlretrieve(url13, "Liste n°13.txt")
urllib.request.urlretrieve(url14, "Liste n°14.txt")
urllib.request.urlretrieve(url15, "Liste n°15.txt")
urllib.request.urlretrieve(url16, "Liste n°16.txt")
urllib.request.urlretrieve(url17, "Liste n°17.txt")
urllib.request.urlretrieve(url18, "Liste n°18.txt")
urllib.request.urlretrieve(url19, "Liste n°19.txt")
urllib.request.urlretrieve(url20, "Liste n°20.txt")
urllib.request.urlretrieve(url21, "Liste n°21.txt")
urllib.request.urlretrieve(url22, "Liste n°22.txt")
urllib.request.urlretrieve(url23, "Liste n°23.txt")
urllib.request.urlretrieve(url24, "Liste n°24.txt")
urllib.request.urlretrieve(url25, "Liste n°25.txt")
urllib.request.urlretrieve(url26, "Liste n°26.txt")
urllib.request.urlretrieve(url27, "Liste n°27.txt")
urllib.request.urlretrieve(url28, "Liste n°28.txt")
urllib.request.urlretrieve(url29, "Liste n°29.txt")
urllib.request.urlretrieve(url30, "Liste n°30.txt")
urllib.request.urlretrieve(url31, "Liste n°31.txt")
urllib.request.urlretrieve(url32, "Liste n°32.txt")
urllib.request.urlretrieve(url33, "Liste n°33.txt")

#On ne garde que les lignes avec sites sur la Liste n°01
with open("Liste n°01.txt") as f:
    lines = f.readlines()
    lines = [l for l in lines if "0.0.0.0" in l]
    with open("Liste n°01a.txt", "w") as f1:
        f1.writelines(lines)  

#On ne garde que les lignes avec sites sur la Liste n°07
with open("Liste n°07.txt") as f2:
    lines = f2.readlines()
    lines = [l for l in lines if "0.0.0.0" in l]
    with open("Liste n°07a.txt", "w") as f3:
        f3.writelines(lines)  
#On ne garde que les lignes avec sites sur la Liste n°10
with open("Liste n°10.txt") as f4:
    lines = f4.readlines()
    lines = [l for l in lines if "127.0.0.1" in l]
    with open("Liste n°10a.txt", "w") as f5:
        f5.writelines(lines)  

#Concaténe la liste des fichiers
filenames = ['Liste n°01a.txt', 'Liste n°02.txt','Liste n°03.txt','liste n°04.txt','Liste n°05.txt','Liste n°06.txt','Liste n°07a.txt','Liste n°08.txt','Liste n°09.txt','Liste n°10a.txt','Liste n°11.txt','Liste n°12.txt','Liste n°13.txt','Liste n°14.txt','Liste n°15.txt','Liste n°16.txt','Liste n°17.txt','Liste n°18.txt','Liste n°19.txt','Liste n°20.txt','Liste n°21.txt','Liste n°22.txt','Liste n°23.txt','Liste n°24.txt','Liste n°25.txt','Liste n°26.txt','Liste n°27.txt','Liste n°28.txt','Liste n°29.txt','Liste n°30.txt','Liste n°31.txt','Liste n°32.txt','Liste n°33.txt']
#dans ce fichier
with open('MasterList.txt', 'w') as outfile:
    for fname in filenames:
        with open(fname) as infile:
            for line in infile:
                outfile.write(line)


#On supprime les caractères inutiles de la Masterliste
with open('MasterList.txt', 'r') as infile, \
     open('MasterListSans.txt', 'w') as outfile:
    data = infile.read()
    data = data.replace("0.0.0.0", "")
    data = data.replace("        ", "")
    data = data.replace("	", "")
    data = data.replace("127.0.0.1", "")
    data = data.replace("www.", "")
    data = data.replace(" ", "")
    outfile.write(data)

#Supprime les lignes qui commencent par un commentaire
import re
input_file = 'MasterListSans.txt'
with open(input_file,"r") as f:
    data = f.read()

data = re.sub(r'#.*', "", data)

with open(input_file, "w") as f:
    f.write(data)

#Supprime les doublons
#Mémorise les lignes déjà lu dans un fichier
lines_seen = set() 

#Défini le fichier de sortie
outfile = open("MasterSansDouble.txt", "w")

#Copie à condition de ne pas être un doublon
for line in open("MasterListSans.txt", "r"):
    if line not in lines_seen:
        outfile.write(line)
        lines_seen.add(line)
outfile.close()

#Créer un dossier avec la date et l'heure du jour

today = datetime.datetime.now()  
os.makedirs(today.strftime("%Y-%m-%d_%H-%M"))

#Déplacer les fichiers intermédiaires
files = ['Liste n°01.txt', 'Liste n°02.txt','Liste n°03.txt','liste n°04.txt','Liste n°05.txt','Liste n°06.txt','Liste n°07a.txt','Liste n°08.txt','Liste n°09.txt','Liste n°10a.txt','Liste n°11.txt','Liste n°12.txt','Liste n°13.txt','Liste n°14.txt','Liste n°15.txt','Liste n°16.txt','Liste n°17.txt','Liste n°18.txt','Liste n°19.txt','Liste n°20.txt','Liste n°21.txt','Liste n°22.txt','Liste n°23.txt','Liste n°24.txt','Liste n°25.txt','Liste n°26.txt','Liste n°27.txt','Liste n°28.txt','Liste n°29.txt','Liste n°30.txt','Liste n°31.txt','Liste n°32.txt','Liste n°33.txt','Liste n°01a.txt','Liste n°07.txt','Liste n°10.txt','MasterList.txt']

for file in files:
    shutil.move(file, today.strftime("%Y-%m-%d_%H-%M"))