#charger les librairies python nécessaire
import requests, time, datetime, os, shutil

def get_file(site, filename):
    target = site
    try: 
        r = requests.get(target, allow_redirects=True)
        open(filename, 'wb').write(r.content)
        return r.status_code
    except requests.exceptions.RequestException as e:
        print("File not downloaded, error: {}".format(e))

#Les petites listes < 100ko
get_file('https://s3.amazonaws.com/lists.disconnect.me/simple_tracking.txt', 'List-A 1.txt')
get_file('https://s3.amazonaws.com/lists.disconnect.me/simple_ad.txt', 'List-A 2.txt')
get_file('https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.Spam/hosts', 'List-A 3.txt')
get_file('https://v.firebog.net/hosts/static/w3kbl.txt', 'List-A 4.txt')
get_file('https://gitlab.com/quidsup/notrack-blocklists/raw/master/notrack-malware.txt', 'List-A 5.txt')
get_file('https://v.firebog.net/hosts/Easylist.txt', 'List-A 6.txt')
get_file('https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=0&mimetype=plaintext', 'List-A 7.txt')
get_file('https://raw.githubusercontent.com/FadeMind/hosts.extras/master/UncheckyAds/hosts', 'List-A 8.txt')
get_file('https://v.firebog.net/hosts/Easyprivacy.txt', 'List-A 9.txt')
get_file('https://v.firebog.net/hosts/Prigent-Ads.txt', 'List-A 10.txt')
get_file('https://zerodot1.gitlab.io/CoinBlockerLists/hosts_browser', 'List-A 11.txt')
get_file('https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.2o7Net/hosts', 'List-A 12.txt')
get_file('https://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/hosts/spy.txt', 'List-A 13.txt')
get_file('https://osint.digitalside.it/Threat-Intel/lists/latestdomains.txt', 'List-A 14.txt')
get_file('https://s3.amazonaws.com/lists.disconnect.me/simple_malvertising.txt', 'List-A 15.txt')
get_file('https://mirror.cedia.org.ec/malwaredomains/immortal_domains.txt', 'List-A 16.txt')
get_file('https://www.malwaredomainlist.com/hostslist/hosts.txt', 'List-A 17.txt')
get_file('https://bitbucket.org/ethanr/dns-blacklists/raw/8575c9f96e5b4a1308f2f12394abd86d0927a4a0/bad_lists/Mandiant_APT1_Report_Appendix_D.txt', 'List-A 18.txt')
get_file('https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.Risk/hosts', 'List-A 19.txt')
get_file('https://urlhaus.abuse.ch/downloads/hostfile/', 'List-A 20.txt')
get_file('https://www.dshield.org/feeds/suspiciousdomains_Medium.txt', 'List-A 21.txt')
get_file('https://www.dshield.org/feeds/suspiciousdomains_High.txt', 'List-A 22.txt')
get_file('https://raw.githubusercontent.com/matomo-org/referrer-spam-blacklist/master/spammers.txt', 'List-A 23.txt')
get_file('https://ssl.bblck.me/blacklists/hosts-file.txt', 'List-A 24.txt')
get_file('https://raw.githubusercontent.com/InnoScorpio/W3C_annual_most_used_survey_blocklist/master/Top500_Domains.txt', 'List-A 25.txt')
get_file('https://raw.githubusercontent.com/Spam404/lists/master/main-blacklist.txt', 'List-A 26.txt')
get_file('https://raw.githubusercontent.com/anudeepND/blacklist/master/facebook.txt', 'List-A 27.txt')
get_file('https://v.firebog.net/hosts/BillStearns.txt', 'List-A 28.txt')
get_file('https://hosts.nfz.moe/basic/hosts', 'List-A 29.txt')
get_file('https://raw.githubusercontent.com/mhhakim/pihole-blocklist/master/list.txt', 'List-A 30.txt')

print("téléchargement des 30 premières listes terminé")

#Les grandes listes > 100ko
get_file('https://mirror1.malwaredomains.com/files/justdomains', 'List-B 1.txt')
get_file('http://sysctl.org/cameleon/hosts', 'List-B 2.txt')
get_file('https://raw.githubusercontent.com/PolishFiltersTeam/KADhosts/master/KADhosts_without_controversies.txt', 'List-B 3.txt')
get_file('https://adaway.org/hosts.txt', 'List-B 4.txt')
get_file('https://gitlab.com/quidsup/notrack-blocklists/raw/master/notrack-blocklist.txt', 'List-B 5.txt')
get_file('https://phishing.army/download/phishing_army_blocklist_extended.txt', 'List-B 6.txt')
get_file('https://v.firebog.net/hosts/AdguardDNS.txt', 'List-B 7.txt')
get_file('https://raw.githubusercontent.com/anudeepND/blacklist/master/adservers.txt', 'List-B 8.txt')
get_file('https://raw.githubusercontent.com/bigdargon/hostsVN/master/hosts', 'List-B 9.txt')
get_file('https://www.github.developerdan.com/hosts/lists/ads-and-tracking-extended.txt', 'List-B 10.txt')
get_file('https://hostfiles.frogeye.fr/firstparty-trackers-hosts.txt', 'List-B 11.txt')
get_file('https://v.firebog.net/hosts/Prigent-Malware.txt', 'List-B 12.txt')
get_file('https://v.firebog.net/hosts/Shalla-mal.txt', 'List-B 13.txt')
get_file('https://www.dshield.org/feeds/suspiciousdomains_Low.txt', 'List-B 14.txt')
get_file('https://hostsfile.org/Downloads/hosts.txt', 'List-B 15.txt')
get_file('https://raw.githubusercontent.com/vokins/yhosts/master/hosts', 'List-B 16.txt')
get_file('https://winhelp2002.mvps.org/hosts.txt', 'List-B 17.txt')
get_file('https://raw.githubusercontent.com/RooneyMcNibNug/pihole-stuff/master/SNAFU.txt', 'List-B 18.txt')
get_file('https://hostsfile.mine.nu/hosts0.txt', 'List-B 19.txt')
get_file('https://www.joewein.net/dl/bl/dom-bl-base.txt', 'List-B 20.txt')
get_file('https://hostfiles.frogeye.fr/multiparty-trackers-hosts.txt', 'List-B 21.txt')
get_file('https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/android-tracking.txt', 'List-B 22.txt')
get_file('https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/SmartTV.txt', 'List-B 23.txt')
get_file('https://v.firebog.net/hosts/Airelle-trc.txt', 'List-B 24.txt')
get_file('https://raw.githubusercontent.com/HorusTeknoloji/TR-PhishingList/master/url-lists.txt', 'List-B 25.txt')
get_file('https://v.firebog.net/hosts/Airelle-hrsk.txt', 'List-B 26.txt')
get_file('https://raw.githubusercontent.com/chadmayfield/my-pihole-blocklists/master/lists/pi_blocklist_porn_top1m.list', 'List-B 27.txt')

print("téléchargement des 27 listes suivantes terminé")

#Très grande list
#get_file('https://raw.githubusercontent.com/chadmayfield/my-pihole-blocklists/master/lists/pi_blocklist_porn_all.list', 'List 62.txt')

#Nécessitant post-traitement
# get_file('https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts', 'List 1.txt')
# get_file('https://raw.githubusercontent.com/DandelionSprout/adfilt/master/Alternate%20versions%20Anti-Malware%20List/AntiMalwareHosts.txt', 'List 28.txt')
# get_file('https://v.firebog.net/hosts/Kowabit.txt', 'List 51.txt')
# get_file('https://adblock.mahakala.is', 'List 52.txt')
# get_file('https://raw.githubusercontent.com/jdlingyu/ad-wars/master/hosts', 'List 53.txt')
# get_file('https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/AmazonFireTV.txt', 'List 58.txt')
# get_file('https://someonewhocares.org/hosts/zero/hosts', 'List 64.txt')

#Concaténe la liste des fichiers
filenamesA = ['List-A 1.txt','List-A 2.txt','List-A 3.txt','List-A 4.txt','List-A 5.txt','List-A 6.txt','List-A 7.txt','List-A 8.txt','List-A 9.txt','List-A 10.txt',
            'List-A 11.txt','List-A 12.txt','List-A 13.txt','List-A 14.txt','List-A 15.txt','List-A 16.txt','List-A 17.txt','List-A 18.txt','List-A 19.txt','List-A 20.txt',
            'List-A 21.txt','List-A 22.txt','List-A 23.txt','List-A 24.txt','List-A 25.txt','List-A 26.txt','List-A 27.txt','List-A 28.txt','List-A 29.txt','List-A 30.txt']

filenamesB = ['List-B 1.txt','List-B 2.txt','List-B 3.txt','List-B 4.txt','List-B 5.txt','List-B 6.txt','List-B 7.txt','List-B 8.txt','List-B 9.txt','List-B 10.txt',
            'List-B 11.txt','List-B 12.txt','List-B 13.txt','List-B 14.txt','List-B 15.txt','List-B 16.txt','List-B 17.txt','List-B 18.txt','List-B 19.txt','List-B 20.txt',
            'List-B 21.txt','List-B 22.txt','List-B 23.txt','List-B 24.txt','List-B 25.txt','List-B 26.txt','List-B 27.txt']

with open('mix_A.txt', 'w') as outfile:
    for fname in filenamesA:
        with open(fname) as infile:
            for line in infile:
                outfile.write(line)

print("regroupement des 30 premières listes terminé")

with open('mix_B.txt', 'w') as outfile:
    for fname in filenamesB:
        with open(fname) as infile:
            for line in infile:
                outfile.write(line)

print("regroupement des 27 listes suivante terminé")

filenamesC = ['mix_A.txt','mix_B.txt']

with open('A+B.txt', 'w') as outfile:
    for fname in filenamesC:
        with open(fname) as infile:
            for line in infile:
                outfile.write(line)

print("regroupement de toutes les listes terminé")

#On supprime les caractères inutiles de Combinaison.txt
with open('A+B.txt', 'r') as infile, \
     open('A+B_net.txt', 'w') as outfile:
    data = infile.read()
    data = data.replace("0.0.0.0", "")
    data = data.replace("        ", "")
    data = data.replace("	", "")
    data = data.replace("127.0.0.1", "")
    data = data.replace("www.", "")
    data = data.replace(" ", "")
    data = data.replace("::", "")
    data = data.replace(":", "")
    outfile.write(data)

print("suppression des caractères inutiles terminé")

#Supprime les lignes qui commencent par un commentaire
import re
input_file = 'A+B_net.txt'
with open(input_file,"r") as f:
    data = f.read()

data = re.sub(r'#.*', "", data)

with open(input_file, "w") as f:
    f.write(data)

print("suppression des lignes avec commentaire terminé")

#Supprime les lignes contenant bad word, c'est a dire des nom de domaine très courant dans la présente liste.

bad_words = ['cable.dyn.cableonline.com.mx','micpn.com','rfksrv.com','truoptik.com','braze.eu','adpredictive.net','hullapp.io','nonstoppartner.net','sendgrid.net','smartclip.net','smartology.net','xsph.ru','appdynamics.com','techtarget.com','infogix.com','insightexpressai.com','247realmedia.com','adsl.net.t-com.hr','swbell.net','sbcglobal.net','duo.carnet.hr','hsd1.tx.comcast.net','ga.comcast.net','online-metrix.net','appnexus.com','akstat.io','adreactor.com','themoneytizer.com','inmobicdn.net','ojrq.net','360safe.com','163.com','bumlam.com','heyzap.com','onesignal.com','qualtrics.com','skimlinks.com','rfihub.com','tapfiliate.com','2cnt.net','backtrace.io','2cnt.net','clickbank.net','meetrics.net','px-cloud.net','adj.st','adsservingtwig.xyz','regularimptracker.xyz','sailthru.com','pingdom.com','pubnub.com','ourtoolbar.com','intellitxt.com','re1.yahoo.com','sp1.yahoo.com','ukl.yahoo.com','scd.yahoo.com','netcabo.pt','dsl.telesp.net.br','pacbell.net','hsd1.fl.comcast.net','neoplus.adsl.tpnet.pl','broadband.hu','res.rr.com','infusionsoft.com','mscnet.com','intercom.io','xg4ken.com','fbcdn.net','ig.com.br','chartboost.com','adtelligent.com','adk2.co','adlightning.com','jivox.com','joystickinteractive.com','omniture.com','optimizely.com','scarabresearch.com','scorecardresearch.com','webtrends.com','ydigitalmedia.com','criteo.net','omtrdc.net','marketingautomation.services','footprintdns.com','mailerlite.com','akamai.net','hitbox.com','top.list.ru','top.mail.ru','wns.windows.com','fbsbx.com','51yes.com','sig-eb.me','web3000.com','adroll.com','clicktale.net','7eer.net','younetmedia.com','mangoads.vn','adnxs.com','clrstm.com','c3metrics.com','clickfunnels.com','igodigital.com','mktoresp.com','naturalbid.com','playziz.com','plista.com','taboola.com','brightedge.com','ampaign.adobe.com','apptimize.com','veinteractive.com','hoverr.media','mobileapptracking.com','kylelierman.com','is-best.net','liveadvert.com','swrve.com','mpstat.us','advertising.com','parsely.com','actonsoftware.com','news-subscribe.com','doubleclick.net','llnwd.net','admarketplace.net','adtdp.com','intellimize.co','apponic.com','casalemedia.com','drift.com','emltrk.com','fiksu.com','keywordblocks.com','marketo.com','motigo.com','ninthdecimal.com','placelocal.com','rockyou.com','socialannex.com','tremorhub.com','weborama.fr','page.link','adglare.net','monetate.net','silveregg.net','go2cloud.org','affex.org','eulerian.net','302br.net','statcounter.com','targetnet.com','2o7.net','civpro.co.za','stofanet.dk','user.ono.com','bezeqint.net','fibernet.hu','cust.tele2.se']

with open('A+B_net.txt') as oldfile, open('A+B_sub.txt', 'w') as newfile:
    for line in oldfile:
        if not any(bad_word in line for bad_word in bad_words):
            newfile.write(line)

print("suppression des subdomain terminé")

#Supprime les doublons
#Mémorise les lignes déjà lu dans un fichier
lines_seen = set() 

#Défini le fichier de sortie
outfile = open("Liste.txt", "w")

#Copie à condition de ne pas être un doublon
for line in open("A+B_sub.txt", "r"):
    if line not in lines_seen:
        outfile.write(line)
        lines_seen.add(line)
outfile.close()

print("suppression des lignes en double terminé")

#Pour ajouter des lignes dans un fichier texte
with open('Liste.txt', 'a') as file:
    #Ajout des domain issu des subdomains
    file.write('\nbroadband.hu\nres.rr.com\ninfusionsoft.com\nmscnet.com\nintercom.io\nxg4ken.com\nfbcdn.net\nig.com.br\nchartboost.com\nadtelligent.com\nadk2.co\nadlightning.com\njivox.com\njoystickinteractive.com\nomniture.com\noptimizely.com\nscarabresearch.com\nscorecardresearch.com\nwebtrends.com\nydigitalmedia.com\ncriteo.net\nomtrdc.net\nmarketingautomation.services\nfootprintdns.com\nmailerlite.com\nakamai.net\nhitbox.com\ntop.list.ru\ntop.mail.ru\nwns.windows.com\nfbsbx.com\n51yes.com\nsig-eb.me\nweb3000.com\nadroll.com\nclicktale.net\n7eer.net\nyounetmedia.com\nmangoads.vn')
    file.write('\nadnxs.com\nclrstm.com\nc3metrics.com\nclickfunnels.com\nigodigital.com\nmktoresp.com\nnaturalbid.com\nplayziz.com\nplista.com\ntaboola.com\nbrightedge.com\nampaign.adobe.com\napptimize.com\nveinteractive.com\nhoverr.media\nmobileapptracking.com\nkylelierman.com\nis-best.net\nliveadvert.com\nswrve.com\nmpstat.us\nadvertising.com\nparsely.com\nactonsoftware.com\nnews-subscribe.com\ndoubleclick.net\nllnwd.net\nadmarketplace.net\nadtdp.com\nintellimize.co\napponic.com\ncasalemedia.com\ndrift.com\nemltrk.com\nfiksu.com\nkeywordblocks.com\nmarketo.com\nmotigo.com\nninthdecimal.com\nplacelocal.com\nrockyou.com\nsocialannex.com\ntremorhub.com\nweborama.fr\npage.link\nadglare.net\nmonetate.net\nsilveregg.net\ngo2cloud.org\naffex.org\neulerian.net\n302br.net\nstatcounter.com\ntargetnet.com\n2o7.net\ncivpro.co.za\nstofanet.dk\nuser.ono.com\nbezeqint.net\nfibernet.hu\ncust.tele2.se')
    file.write('\nonline-metrix.net\nappnexus.com\nakstat.io\nadreactor.com\nthemoneytizer.com\ninmobicdn.net\nojrq.net\n360safe.com\n163.com\nbumlam.com\nheyzap.com\nonesignal.com\nqualtrics.com\nskimlinks.com\nrfihub.com\ntapfiliate.com\n2cnt.net\nbacktrace.io\n2cnt.net\nclickbank.net\nmeetrics.net\npx-cloud.net\nadj.st\nadsservingtwig.xyz\nregularimptracker.xyz\nsailthru.com\npingdom.com\npubnub.com\nourtoolbar.com\nintellitxt.com\nre1.yahoo.com\nsp1.yahoo.com\nukl.yahoo.com\nscd.yahoo.com\nnetcabo.pt\ndsl.telesp.net.br\npacbell.net\nhsd1.fl.comcast.net\nneoplus.adsl.tpnet.pl')
    file.write('\nmicpn.com\nrfksrv.com\ntruoptik.com\nbraze.eu\nadpredictive.net\nhullapp.io\nnonstoppartner.net\nsendgrid.net\nsmartclip.net\nsmartology.net\nxsph.ru\nappdynamics.com\ntechtarget.com\ninfogix.com\ninsightexpressai.com\n247realmedia.com\nadsl.net.t-com.hr\nswbell.net\nsbcglobal.net\nduo.carnet.hr\nhsd1.tx.comcast.net\nga.comcast.net\ncable.dyn.cableonline.com.mx')
    #Ajout de la liste personnelle de blocage
    file.write('\nonclickalgo.com\nonclickperformance.com\nonclickgenius.com\nseaboblit.com\ndig.bdurl.net\nuanalysys.cn\ngetui.com\nhicloud.com\ndns.weixin.qq.com\nlf.snssdk.com\nixigua.com\npstatp.com\ndouyincdn.com')

#Créer un dossier avec la date et l'heure du jour
today = datetime.datetime.now()  
os.makedirs(today.strftime("%Y-%m-%d_%H-%M"))

#Déplacer les fichiers intermédiaires
files = ['List-A 1.txt','List-A 2.txt','List-A 3.txt','List-A 4.txt','List-A 5.txt','List-A 6.txt','List-A 7.txt','List-A 8.txt','List-A 9.txt','List-A 10.txt',
            'List-A 11.txt','List-A 12.txt','List-A 13.txt','List-A 14.txt','List-A 15.txt','List-A 16.txt','List-A 17.txt','List-A 18.txt','List-A 19.txt','List-A 20.txt',
            'List-A 21.txt','List-A 22.txt','List-A 23.txt','List-A 24.txt','List-A 25.txt','List-A 26.txt','List-A 27.txt','List-A 28.txt','List-A 29.txt','List-A 30.txt',
            'List-B 1.txt','List-B 2.txt','List-B 3.txt','List-B 4.txt','List-B 5.txt','List-B 6.txt','List-B 7.txt','List-B 8.txt','List-B 9.txt','List-B 10.txt',
            'List-B 11.txt','List-B 12.txt','List-B 13.txt','List-B 14.txt','List-B 15.txt','List-B 16.txt','List-B 17.txt','List-B 18.txt','List-B 19.txt','List-B 20.txt',
            'List-B 21.txt','List-B 22.txt','List-B 23.txt','List-B 24.txt','List-B 25.txt','List-B 26.txt','List-B 27.txt','mix_A.txt','mix_B.txt','A+B.txt','A+B_net.txt','A+B_sub.txt']
for file in files:
    shutil.move(file, today.strftime("%Y-%m-%d_%H-%M"))