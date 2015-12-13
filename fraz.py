#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators
import re
from pywikibot import xmlreader
import datetime
import collections
from klasa import *

def fraz(data):

    data_slownie = data[6] + data[7] + '.' + data[4] + data[5] + '.' + data[0] + data[1] + data[2] + data[3]
    lista_stron = getListFromXML(data)
    site = pywikibot.Site('pl', 'wiktionary')
    outputPage = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/listy/związki_frazeologiczne')

    tempLangs = []

    notFound = []
    text = 'Hasła, które określone zostały jako związek frazeologiczny, lecz nie widnieją w indeksie związków frazeologicznych odpowiednim dla danego języka. Ostatnia aktualizacja: %s\n' % (data_slownie)
    phraseList = {}
    notFoundList = collections.defaultdict(list)

    LangsMediaWiki = getAllLanguages()

    # prepare a dictionary of phrase indexes. If an index page doesn't exist
    # assign a blank page to it

    for a in LangsMediaWiki:
        #print a.shortName
        indexPageName = 'Indeks:{0}_-_Związki_frazeologiczne'.format(a.upperName)
        
        try: phraseList[a.shortName] = pywikibot.Page(site, indexPageName).get()
        except pywikibot.NoPage:
            phraseList['%s' % a.shortName] = ''
        except pywikibot.IsRedirectPage:
            print('redirect')

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
                    if lang.type != 2:
                        lang.pola()
                    try: lang.subSections['znaczenia'].text
                    except AttributeError:
                        continue
                    else:
                        if lang.type != 2 and 'związek frazeologiczny' in lang.subSections['znaczenia'].text and '[[{0}]]'.format(word.title) not in phraseList[lang.lang]:
                            notFoundList['%s' % lang.lang].append(word.title)

    for a in LangsMediaWiki:
        if notFoundList['%s' % a.shortName]:
            text += '== [[Indeks:%s_-_Związki_frazeologiczne|%s]] ==' % (a.upperName, a.longName)
            for b in notFoundList['%s' % a.shortName]:
                text += '\n*[[%s]] <nowiki>| *[[%s]]</nowiki> →' % (b, b)
            text += '\n'

    with open('output/fraz.txt', encoding='utf-8', mode='w') as f:
        f.write(text)

    outputPage.text = text
    outputPage.save(comment="Aktualizacja listy", botflag=False)
