#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
import pywikibot
import re
import config
from os import environ
from klasa import *
from sjpClass import kategoriaSlowa, checkHistory


def checkIfExists(page):
	
        initial_length = len(page.listLangs)
        def determine(section):
                try: check = Haslo(section.titleHeader)
		except sectionsNotFound:
			pass
		except WrongHeader:
			pass
		else:
			if check.type == 3:
				for elem in check.listLangs:
					if elem.lang == u'polski':
                                                return 1
                return 0

    initial_length = len(page.listLangs)
    def determine(section):
        try: check = Haslo(section.titleHeader)
        except sectionsNotFound:
            pass
        except WrongHeader:
            pass
        else:
            if check.type == 3:
                for elem in check.listLangs:
                    if elem.lang == 'polski':
                        return 1
        return 0

    page.listLangs[:] = [x for x in page.listLangs if not determine(x)]

    if len(page.listLangs) != initial_length:
        return 1
    return 0

def createMapping(map):
    mapPage = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/sjp/mapa')
    wordListFilename = '%soutput/frequencyListPL.txt' % config.path['scripts']
    wordList = codecs.open(wordListFilename, 'r', 'utf-8')
    i=1
    table = '{| class="wikitable"'
    for line in wordList:
        word = line.strip().split('=')[0]
        if i>500:
            break
        try: map[word]
        except KeyError:
            pass
        else:
            if '\n|-\n|%s\n|[[' % word not in table:
                table += '\n|-\n|%s\n|[[%s|%s]]' % (word, map[word], map[word].replace('Wikipedysta:AlkamidBot/sjp/', ''))
                i+=1
    table += '\n|-\n|}'
    mapPage.put(table, comment='aktualizacja')

def checkImages(page, obrazki):
    changed = 0
    for sekcja in page.listLangs:
        for obr in obrazki:
            if obr == sekcja.title or '%s się' % obr == sekcja.title:
                if checkHistory('%s%d' % (kat.pages, i+1)):
                    sekcja.pola()
                    for a in obrazki[obr]:
                        if a not in sekcja.dodatki.text:
                            sekcja.dodatki.text += '\n%s' % (a)
                            sekcja.saveChanges()
                            changed = 1
    return changed

def updateTable(katPages, pageCount, tableText):
    page = pywikibot.Page(site, '%s%d' % (katPages, pageCount))
    history = page.getVersionHistory()
    if history[0][2] == 'Olafbot' and history[0][3] == 'Zawartość została przeniesiona do artykułów.':
        tableText = tableText.replace('\n| [[%s%d|%d]]' % (katPages, pageCount, pageCount), '')
    return tableText

def main():
    global site
    site = pywikibot.Site()
    wordsPerPage = 10

    kategorie = []
    kategorie.append(kategoriaSlowa('bezproblemu', wordsPerPage, 'łatwe/', '\n|-\n| łatwe (jedno znaczenie, bez synonimów)', 'bezproblemu'))
    kategorie.append(kategoriaSlowa('zwrotne', wordsPerPage, 'zwrotne/', '\n|-\n| czasowniki zwrotne', 'zwrotne'))
    ##kategorie.append(kategoriaSlowa(u'ndm', wordsPerPage, u'ndm/', u'\n|-\n| nieodmienne', u'ndm'))
    kategorie.append(kategoriaSlowa('np', wordsPerPage, 'np/', '\n|-\n| \"np.\" w znaczeniu', 'np'))
    kategorie.append(kategoriaSlowa('reszta', wordsPerPage, 'wszystkie/', '\n|-\n| reszta', 'reszta'))
    kategorie.append(kategoriaSlowa('brak_znaczenia', wordsPerPage, 'brak_znaczen/', '\n|-\n| bez znaczeń', 'brak_znaczenia'))
    kategorie.append(kategoriaSlowa('przymiotnik_od', wordsPerPage, 'przymiotnik_od/', '\n|-\n| \"przymiotnik od\"', 'przymiotnik_od'))

    tabelkaPage = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/sjp/tabelka')
    tabText = tabelkaPage.get()
    for kat in kategorie:
        s_limits = re.search(r'%s([0-9]{1,2}?)\|[0-9]{1,2}]]\n\|(?=-|\})' % kat.pages, tabText)
        if s_limits:
            kat.addLimit(int(s_limits.group(1)))
    obrazki = obrazkiAndrzeja()

    mapping = {}

    for kat in kategorie:
        for i in range(kat.limit):
            try: haslo = Haslo('%s%d' % (kat.pages, i+1))
            except sectionsNotFound:
                tabText = updateTable(kat.pages, i+1, tabText)
            else:
                if haslo.type == 3:
                    comment = ''
                    if checkIfExists(haslo):
                        comment += 'usunięcie istniejącego hasła'
                    if checkImages(haslo, obrazki):
                        comment += ', dodanie ilustracji z [[Wikipedysta:Andrzej 22/Ilustracje|listy Andrzeja]]'
                    comment.strip(', ')
                    if comment != '':
                        haslo.push(False, comment)

                    if kat.name != 'brak_znaczenia':
                        for sekcja in haslo.listLangs:
                            mapping[sekcja.titleHeader] = '%s%d' % (kat.pages, i+1)

    tabelkaPage.put(tabText, 'aktualizacja')
    createMapping(mapping)


if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
        

