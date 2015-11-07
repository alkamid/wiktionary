#!/usr/bin/python
# -*- coding: utf-8 -*-

'''This script counts page visits on the previous day. pagecounts files available from dumps.wikimedia.org are split in hours so this
is basically to sum data from 24 files, sort them in decreasing order and put on pl.wikt'''
import codecs
import os
import glob #need this to remove files
import subprocess
import pywikibot
import urllib.request, urllib.parse, urllib.error
import datetime
import gzip
import config
from operator import itemgetter

def checkSum(folder, filename, dateString):
    urlmd5 = 'http://dumps.wikimedia.org/other/pagecounts-raw/%s/%s-%s/md5sums.txt' % (dateString[:4], dateString[:4], dateString[4:6])
    md5 = urllib.request.urlopen(urlmd5)
    sum = None
    for line in md5:
        if filename in line:
            sum = line.split()[0]
    if sum:
        sumDownloaded = subprocess.check_output(["md5sum", folder+filename])[:32]
        if sum == sumDownloaded:
            return 1
        else:
            return 0
    else:
        return 0

def main():
    #get the default site - the bot is operating on pl.wikt only
    site = pywikibot.Site()

    #a list and a dict to handle individual entries
    lista = []
    rankingDict = {}

    #control how many entries should appear on the stats site
    limitEntriesTo = 1000

    date_yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    date_string = date_yesterday.strftime("%Y%m%d")
    data_slownie = date_string[6] + date_string[7] + '.' + date_string[4] + date_string[5] + '.' + date_string[0] + date_string[1] + date_string[2] + date_string[3]

    statSite = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/statystyka/wizyty')

    for hour in range(24):

        for seconds in range(25):

            folder = config.path['pagecounts']
            filename = '{0}/{1}-{2}/pagecounts-{3}-{4:02d}00{5:02d}.gz'.format(date_string[:4], date_string[:4], date_string[4:6], date_string, hour, seconds)
            try: inp = gzip.open(folder + filename, mode='rt')
            except IOError:
                continue

            #here was the code used for downloading pagecounts, moved to the end of this file

        try:
            for line in inp:
                
                #only process lines starting with "pl.d" which means pl.wiktionary
                if line[:4] == 'pl.d':
                    
                    #the lines should look like this: pl.d pagename visits size, where size is the size of the content returned
                    a = line.split()

                    #convert %-escaped characters to utf-8
                    a[1] = urllib.parse.unquote(a[1])
                    
                    #if the page is not in the dictionary, add it with the initial count; if it is in dictionary, sum the visits
                    rankingDict[a[1]] = rankingDict.get(a[1], 0) + int(a[2])
        except IOError:
            pass
        #print(hour) #- just for debugging, shows which hour we are in
        inp.close

    ranking = sorted(list(rankingDict.items()), key=itemgetter(1), reverse=True)

    text = 'Statystyka wizyt na stronach z %s. Nie obejmuje przestrzeni nazw: Plik, Szablon, Specjalna, Kategoria, Dyskusja Wikipedysty.' % data_slownie
    text += '\n\n{| class="wikitable sortable"\n|-\n!strona\n!odwiedzin'
    textFile = ''

    i = 0
    for a in ranking:
        if (i<limitEntriesTo) and 'Plik:' not in a[0] and 'Szablon:' not in a[0] and 'Specjalna:' not in a[0] and 'Kategoria:' not in a[0] and 'Special:' not in a[0] and 'Dyskusja Wikipedysty:' not in a[0] and 'admin/' not in a[0]:
            textFile = textFile + '\n%s|%d' % (a[0], a[1])
            text = text + '\n|-\n|[[%s]]\n|%d' % (a[0], a[1])
            i += 1

    text += '\n|}'
    text = text.replace('_', ' ')

    with open('{0}output/visits.txt'.format(config.path['scripts']), encoding='utf-8', mode='w') as f:
        f.write(textFile)
    
    statSite.text = text
    statSite.save(comment = 'aktualizacja', botflag=False)

    #cleanup  - only if you download files along the way
    '''os.chdir('/mnt/user-store/alkamid/stats/')
    toRemove= glob.glob('pagecounts*.gz')
    for file in toRemove:
            os.remove(file)'''

if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
