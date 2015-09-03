#!/usr/bin/python
# -*- coding: utf-8 -*-

# szuka danego przez szukany_tekst wyrażenia w hasłach

import sqlite3
from pywikibot import Category
import pywikibot
from pywikibot import pagegenerators
import re
from pywikibot import xmlreader
from klasa import *

def main():

    data = '20120216'
    con = sqlite3.connect('../sqlite.db')
    f = open('/mnt/user-store/dumps/plwiktionary/plwiktionary-%s-pagelinks.sql' % data,'r')
    sql = f.read() # watch out for built-in `str`
    print(sql[:10000])
    cur = con.cursor()
    cur.executescript(sql)
    '''
    lista_stron1 = xmlreader.XmlDump('/mnt/user-store/dumps/plwiktionary/plwiktionary-%s-pages-articles.xml' % data)
    lista_stron2 = xmlreader.XmlDump.parse(lista_stron1)
    text = u''
    rere = re.compile(ur'[0-9]\.[0-9]')
    #t = codecs.open('/home/alkamid/wikt/moje/input/forma.txt', 'r', 'utf-8')
    ranking = []
    #for line in t:
    #    ranking.append(line.strip())


    for a in lista_stron2:
        if int(a.revisionid) > 2646076 and a.username not in ('Olafbot', 'AlkamidBot', 'KamikazeBot', 'MastiBot', 'Luckas-bot', 'Agnese'):
            try: h = Haslo(a.title, a.text)
            except sectionsNotFound:
                pass
            except WrongHeader:
                pass
            else:
                if h.type == 3:
                    for elem in h.listLangs:
                        if elem.lang not in ('polski', 'arabski'):
                            ranking.append([elem.title, len(elem.content)])

    def sortkey(row):
        return float(row[1])

    ranking.sort(key=sortkey, reverse=True)
    for i in range(50):
        print ranking[i][0]'''


    #for p in lista_stron2:
    #    if any (item in p.text for item in lista):
    #        print u'*[[%s]]' % p.title

if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
