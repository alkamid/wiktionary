#!/usr/bin/python
# -*- coding: utf-8 -*-

# robienie listy haseł polskich bez wymowy

import sys
sys.path.append('/home/adam/wikt/pywikipedia')
import codecs
from pywikibot import Category
import pywikibot
from pywikibot import pagegenerators
import re
from pywikibot import xmlreader
from klasa import *

def countMean():

    global data
    data = '20110502'
    lista_stron1 = xmlreader.XmlDump('plwiktionary-%s-pages-articles.xml' % data)
    lista_stron = xmlreader.XmlDump.parse(lista_stron1)

    re_count = re.compile('(\: \([0-9]\.[0-9]\))')
    counter = 0

    text = ''
    lista = []

    for page in lista_stron:
        word = Haslo(page.title, page.text)
        if word.type == 3:
            for lang in word.listLangs:
                if lang.type == 1:
                    lang.pola()
                    if lang.znaczeniaWhole:
                        if lang.type == 7:
                            temp = []
                            temp.append(lang.lang)
                            temp.append(word.title)
                            lista.append(temp)

    def sortkey(row):
        return row[0]

    lista.sort(key=sortkey)
    for a in lista:
        text = text + '* [[%s]] (%s)\n' % (a[1], a[0])

    file = open("output/brak_części_mowy.txt", 'a')
    file.write (text.encode("utf-8"))
    file.close



if __name__ == '__main__':
    try:
        countMean()
    finally:
        pywikibot.stopme()
