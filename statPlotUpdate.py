from datetime import date, timedelta

import upload
import pywikibot
from bs4 import BeautifulSoup
import requests

from statPlot import monthly_stat_plot

def update():

    old_main_url = 'https://pl.wiktionary.org/w/index.php?title=Wikis%C5%82ownik:Strona_g%C5%82%C3%B3wna&oldid=2639658'

    r = requests.get(old_main_url)
    soup = BeautifulSoup(r.content, 'lxml')

    stat_paragraphs_str = soup.table.find_all('td')[2].div.div.find_all('p')
    num_entries, num_pages = [int(p.b.contents[0].replace('\xa0', '')) for p in stat_paragraphs_str]

    entry = '%.1f' % (num_entries/1000.0)
    page = '%.1f' % (num_pages/1000.0)

    dateToday = date.today()
    dateEarlier = dateToday - timedelta(days=5)

    with open("stat-data.csv", "a+") as myfile:
        myfile.seek(0)
        last_line = myfile.readlines()[-1].split(',')
        if last_line[0] != dateEarlier.strftime('%m-%Y'):
            myfile.write("%s,%s,%s\n" % (dateEarlier.strftime("%m-%Y"), page, entry))

    monthly_stat_plot()

    targetFilename = 'Wzrost_Wikislownika.svg'
    fname = 'Wzrost_Wikislownika.svg'
    desc = 'update (%s)' % dateEarlier.strftime("%Y/%m")

    bot = upload.UploadRobot([targetFilename], description=desc, keepFilename=True, verifyDescription=False, ignoreWarning=True, targetSite=pywikibot.Site('commons', 'commons'))
    bot.run()

update()
