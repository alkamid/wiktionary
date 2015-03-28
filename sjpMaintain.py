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

        page.listLangs[:] = [x for x in page.listLangs if not determine(x)]
        
        if len(page.listLangs) != initial_length:
                return 1
	return 0

def createMapping(map):
	mapPage = pywikibot.Page(site, u'Wikipedysta:AlkamidBot/sjp/mapa')
	wordListFilename = u'%soutput/frequencyListPL.txt' % config.path['scripts']
	wordList = codecs.open(wordListFilename, 'r', 'utf-8')
	i=1
	table = u'{| class="wikitable"'
	for line in wordList:
		word = line.strip().split('=')[0]
		if i>500:
			break
		try: map[word]
		except KeyError:
			pass
		else:
			if u'\n|-\n|%s\n|[[' % word not in table:
				table += u'\n|-\n|%s\n|[[%s|%s]]' % (word, map[word], map[word].replace(u'Wikipedysta:AlkamidBot/sjp/', u''))
				i+=1
	table += u'\n|-\n|}'
	mapPage.put(table, comment=u'aktualizacja')

def checkImages(page, obrazki):
	changed = 0
	for sekcja in page.listLangs:
		for obr in obrazki:
			if obr == sekcja.title or u'%s się' % obr == sekcja.title:
				if checkHistory(u'%s%d' % (kat.pages, i+1)):
					sekcja.pola()
					for a in obrazki[obr]:
						if a not in sekcja.dodatki.text:
							sekcja.dodatki.text += u'\n%s' % (a)
							sekcja.saveChanges()
							changed = 1
	return changed

def updateTable(katPages, pageCount, tableText):
	page = pywikibot.Page(site, u'%s%d' % (katPages, pageCount))
	history = page.getVersionHistory()
	if history[0][2] == u'Olafbot' and history[0][3] == u'Zawartość została przeniesiona do artykułów.':
		tableText = tableText.replace(u'\n| [[%s%d|%d]]' % (katPages, pageCount, pageCount), u'')
	return tableText
							
def main():
	global site
	site = pywikibot.Site()
	wordsPerPage = 10
	
	kategorie = []
	kategorie.append(kategoriaSlowa(u'bezproblemu', wordsPerPage, u'łatwe/', u'\n|-\n| łatwe (jedno znaczenie, bez synonimów)', u'bezproblemu'))
	kategorie.append(kategoriaSlowa(u'zwrotne', wordsPerPage, u'zwrotne/', u'\n|-\n| czasowniki zwrotne', u'zwrotne'))
	##kategorie.append(kategoriaSlowa(u'ndm', wordsPerPage, u'ndm/', u'\n|-\n| nieodmienne', u'ndm'))
	kategorie.append(kategoriaSlowa(u'np', wordsPerPage, u'np/', u'\n|-\n| \"np.\" w znaczeniu', u'np'))
	kategorie.append(kategoriaSlowa(u'reszta', wordsPerPage, u'wszystkie/', u'\n|-\n| reszta', u'reszta'))
	kategorie.append(kategoriaSlowa(u'brak_znaczenia', wordsPerPage, u'brak_znaczen/', u'\n|-\n| bez znaczeń', u'brak_znaczenia'))
	kategorie.append(kategoriaSlowa(u'przymiotnik_od', wordsPerPage, u'przymiotnik_od/', u'\n|-\n| \"przymiotnik od\"', u'przymiotnik_od'))
	
	tabelkaPage = pywikibot.Page(site, u'Wikipedysta:AlkamidBot/sjp/tabelka')
	tabText = tabelkaPage.get()
	for kat in kategorie:
                s_limits = re.search(ur'%s([0-9]{1,2}?)\|[0-9]{1,2}]]\n\|(?=-|\})' % kat.pages, tabText)
		if s_limits:
			kat.addLimit(int(s_limits.group(1)))
	obrazki = obrazkiAndrzeja()
	
	mapping = {}		
	
	for kat in kategorie:
                print kat.limit

		for i in range(kat.limit):
			try: haslo = Haslo(u'%s%d' % (kat.pages, i+1))
			except sectionsNotFound:
				tabText = updateTable(kat.pages, i+1, tabText)
			else:
				if haslo.type == 3:
					comment = u''
					if checkIfExists(haslo):
						comment += u'usunięcie istniejącego hasła'
					if checkImages(haslo, obrazki):
						comment += u', dodanie ilustracji z [[Wikipedysta:Andrzej 22/Ilustracje|listy Andrzeja]]'
					comment.strip(u', ')
					if comment != u'':
						haslo.push(False, comment)
				              
					if kat.name != u'brak_znaczenia':
						for sekcja in haslo.listLangs:
							mapping[sekcja.titleHeader] = u'%s%d' % (kat.pages, i+1)
						
	tabelkaPage.put(tabText, u'aktualizacja')
	createMapping(mapping)
	
	
if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
        

