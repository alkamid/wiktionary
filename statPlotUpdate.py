import urllib2
from lxml import etree, html
from datetime import date, timedelta
from subprocess import call
import upload
import pywikibot

def update():
    
    oldMainURL = u'https://pl.wiktionary.org/w/index.php?title=Wikis%C5%82ownik:Strona_g%C5%82%C3%B3wna&oldid=2639658'
    
    toParse = urllib2.urlopen(oldMainURL)
    doc = etree.parse(toParse)
    toParse.close()

    entryNum =  int(doc.xpath('//td[@class="sg_ramka"]/div/div[1]/p/a/font/b/text()')[0].replace(u'\xa0', ''))
    pageNum =  int(doc.xpath('//td[@class="sg_ramka"]/div/div[1]/p/b/text()')[0].replace(u'\xa0', ''))

    entry = '%.1f' % (entryNum/1000.0)
    page = '%.1f' % (pageNum/1000.0)

    dateToday = date.today()
    dateEarlier = dateToday - timedelta(days=5)

    with open("stat-data.dat", "a") as myfile:
        myfile.write("%s\t%s\t%s\n" % (dateEarlier.strftime("%m-%Y"), page, entry))

    call(["gnuplot", "wikislownik.plt"])
    
    targetFilename = 'Wzrost_Wikislownika.svg'
    fname = 'Wzrost_Wikislownika.svg'
    desc = 'update (%s)' % dateEarlier.strftime("%Y/%m")

    bot = upload.UploadRobot(targetFilename, description=desc, useFilename=fname, keepFilename=True, verifyDescription=False, ignoreWarning=True, targetSite=pywikibot.getSite('commons', 'commons'))
    bot.run()


update()
