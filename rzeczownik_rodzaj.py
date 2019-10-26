#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators
import re
from pywikibot import xmlreader
import collections
from klasa import *

def rzeczownikRodzaj(data):

    data_slownie = data[6] + data[7] + '.' + data[4] + data[5] + '.' + data[0] + data[1] + data[2] + data[3]
    lista_stron = getListFromXML(data)
    wikt = pywikibot.Site('pl', 'wiktionary')
    outputPage1 = pywikibot.Page(wikt, 'Wikipedysta:AlkamidBot/listy/rodzaj/1')
    outputPage2 = pywikibot.Page(wikt, 'Wikipedysta:AlkamidBot/listy/rodzaj/2')
    noGenderPage = pywikibot.Page(wikt, 'Wikipedysta:AlkamidBot/listy/rodzaj/wykluczone')

    forbidden = noGenderPage.get()
    forbiddenList = forbidden.split('\n')
    del forbiddenList[0]
    forbiddenList.remove('')
    for a in forbiddenList:
        a = a.strip()

    tempLangs = []

    notFound = []
    lenTest = ''
    text = 'Lista słów (część pierwsza), w których w sekcji "znaczenia" występuje "rzeczownik", lecz nie ma rodzaju. Dane z %s. Jeśli znajduje się tu język, w którym rzeczowniki nie mają rodzaju, dodaj go [[Wikipedysta:AlkamidBot/listy/rodzaj/wykluczone|tutaj]].\n[[Wikipedysta:AlkamidBot/listy/rodzaj/2|Część druga]].\n' % (data_slownie)
    text2 = 'Lista słów (część druga), w których w sekcji "znaczenia" występuje "rzeczownik", lecz nie ma rodzaju. Dane z %s. Jeśli znajduje się tu język, w którym rzeczowniki nie mają rodzaju, dodaj go [[Wikipedysta:AlkamidBot/listy/rodzaj/wykluczone|tutaj]].\n[[Wikipedysta:AlkamidBot/listy/rodzaj/1|Część pierwsza]]\n' % (data_slownie)
    notFoundList = collections.defaultdict(list)

    LangsMediaWiki = getAllLanguages()
    gwary = ['{{poznań}}', '{{białystok}}', '{{częstochowa}}', 'gwara więzienna', '{{gwara}}', '{{góry}}', '{{kielce}}', '{{kraków}}', '{{kresy}}', '{{kujawy}}', '{{lwów}}', '{{mazowsze}}', '{{reg', '{{regionalizm', '{{warmia}}', '{{warszawa}}', '{{łódź}}', '{{śląsk}}']
    allNounsCount= {}
    for a in LangsMediaWiki:
        allNounsCount[a.shortName] = 0

    # list of languages in which plural-only nouns do not have gender
    plural_no_gender_langs = ('jidysz', 'niemiecki')

    for a in lista_stron:
        try: word = Haslo(a)
        except sectionsNotFound:
            pass
        except WrongHeader:
            pass
        else:
            if word.type == 3:
                for lang in word.listLangs:
                    if lang.type != 2 and lang.lang not in forbiddenList:
                        lang.pola()
                        if lang.type == 1:
                            for d in lang.znaczeniaDetail:
                                if 'rzeczownik' in d[0] and '{{forma rzeczownika' not in d[0]:
                                    if 'liczba mnoga' in d[0] and lang.lang in plural_no_gender_langs:
                                        continue
                                    try: allNounsCount['%s' % lang.lang] += 1
                                    except KeyError:
                                        pass
                                    if 'rodzaj' not in d[0]:
                                        #gwara = 0
                                        #for gw in gwary:
                                        #       if gw in d[1]:
                                        #               gwara = 1
                                        #if not gwara and word.title[-1] != u'a' and word.title[-3:] != u'cki' and word.title[-3:] != u'ski':
                                        notFoundList['%s' % lang.lang].append(word.title)

    for a in LangsMediaWiki:
        if notFoundList['%s' % a.shortName] and a.shortName not in forbiddenList[0]:
            lenTest += '== %s ==' % (a.longName)
            for b in notFoundList['%s' % a.shortName]:
                lenTest += '\n*[[%s]]' % (b)
            lenTest += '\n'

    lenHalf = len(lenTest)/2

    for a in LangsMediaWiki:
        if notFoundList['%s' % a.shortName] and a.shortName not in forbiddenList[0]:
            if len(text) < lenHalf:
                text += '== %s ==' % (a.longName)
                text += '\nRodzaju nie posiada \'\'\'%.1f%%\'\'\' rzeczowników' % (float(len(notFoundList[a.shortName]))/float(allNounsCount[a.shortName])*100.0)

                for b in notFoundList['%s' % a.shortName]:
                    text += '\n*[[%s]]' % (b)
                text += '\n'
            else:
                text2 += '== %s ==' % (a.longName)
                text2 += '\nRodzaju nie posiada \'\'\'%.1f%%\'\'\' rzeczowników' % (float(len(notFoundList[a.shortName]))/float(allNounsCount[a.shortName])*100.0)
                for b in notFoundList['%s' % a.shortName]:
                    text2 += '\n*[[%s]]' % (b)
                text2 += '\n'

                
    with open('output/bez_rodzaju_1.txt', encoding='utf-8', mode='w') as f:
        f.write(text)

    with open('output/bez_rodzaju_2.txt', encoding='utf-8', mode='w') as f:
        f.write(text2)

    outputPage1.text = text
    outputPage2.text = text2

    outputPage1.save(comment="Aktualizacja listy", botflag=False)
    outputPage2.save(comment="Aktualizacja listy", botflag=False)
