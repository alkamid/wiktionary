#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators
import re
from pywikibot import xmlreader
import collections
from klasa import *

def brakCzesciMowy(data):

    data_slownie = data[6] + data[7] + '.' + data[4] + data[5] + '.' + data[0] + data[1] + data[2] + data[3]
    lista_stron = getListFromXML(data)
    wikt = pywikibot.Site('pl', 'wiktionary')
    outputPage = pywikibot.Page(wikt, 'Wikipedysta:AlkamidBot/listy/części_mowy')

    tempLangs = []

    notFound = []
    text = 'Do poniższych haseł nie wpisano, jakimi są częściami mowy - jeśli potrafisz, zrób to. Ostatnia aktualizacja wg zrzutu bazy danych z %s.\n' % (data_slownie)
    notFoundList = collections.defaultdict(list)

    LangsMediaWiki = getAllLanguages()

    with open('output/missing_pos.txt', 'w') as f:
        for a in lista_stron:
            try: word = Haslo(a)
            except notFromMainNamespace:
                pass
            except sectionsNotFound:
                pass
            except WrongHeader:
                pass
            else:
                if word.type == 3:
                    for lang in word.listLangs:
                        if lang.type != 2 and lang.type != 7:
                            lang.pola()
                            if lang.type == 5:
                                notFoundList['%s' % lang.lang].append(lang.title)
                                print(lang.title)
                                f.write(lang.title + '\n')

    for a in LangsMediaWiki:
        if notFoundList['%s' % a.shortName]:
            text += '== %s ==' % (a.longName)
            for b in notFoundList['%s' % a.shortName]:
                text += '\n*[[%s]]' % (b)
            text += '\n'

    with open('output/missing_pos.txt', 'w') as f:
        f.write(text)

    outputPage.text = text
    outputPage.save(comment="Aktualizacja listy", botflag=False)
