# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators
import re
from pywikibot import xmlreader
import datetime
import collections
from klasa import *

def fraz(data):

    data_slownie = data[6:8] + '.' + data[4:6] + '.' + data[0:4]

    lista_stron = getListFromXML(data)
    wikt = pywikibot.Site('pl', 'wiktionary')
    outputPage = pywikibot.Page(wikt, 'Wikipedysta:AlkamidBot/listy/związki_frazeologiczne')

    tempLangs = []

    notFound = []
    text = 'Hasła, które określone zostały jako związek frazeologiczny, lecz nie widnieją w indeksie związków frazeologicznych odpowiednim dla danego języka. Ostatnia aktualizacja: %s\n' % (data_slownie)
    phraseList = {}
    notFoundList = collections.defaultdict(list)

    LangsMediaWiki = getAllLanguages()

    for a in LangsMediaWiki:
        indexPageName = 'Indeks:%s_-_Związki_frazeologiczne' % a.upperName
        try:
            ifExists = pywikibot.Page(wikt, indexPageName).get()
        except pywikibot.NoPage:
            phraseList['%s' % a.shortName] = ''
        except pywikibot.IsRedirectPage:
            print('redirect')
        else:
            phraseList['%s' % a.shortName] = ifExists


    for a in lista_stron:
        try: word = Haslo(a)
        except notFromMainNamespace:
            continue
        except sectionsNotFound:
            continue
        except WrongHeader:
            continue
        else:
            if word.type == 3:
                
                for lang in word.listLangs:
                    if lang.type != 2:
                        lang.pola()
                    try: lang.subSections['znaczenia'].text
                    except AttributeError:
                        pass
                    except KeyError:
                        print('{0} / {1}: znaczenia not found'.format(word.title, listLangs.lang))
                    else:
                        if lang.type != 2 and 'związek frazeologiczny' in lang.subSections['znaczenia'].text and '[[%s]]' % word.title not in phraseList['%s' % lang.lang]:
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
    
