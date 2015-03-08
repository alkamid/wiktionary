#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators
import re
from pywikibot import xmlreader
import collections
from klasa import *

def rzeczownikRodzaj(data):

	data_slownie = data[6] + data[7] + u'.' + data[4] + data[5] + u'.' + data[0] + data[1] + data[2] + data[3]
	lista_stron = getListFromXML(data)
	wikt = pywikibot.Site('pl', 'wiktionary')
	outputPage1 = pywikibot.Page(wikt, u'Wikipedysta:AlkamidBot/listy/rodzaj/1')
	outputPage2 = pywikibot.Page(wikt, u'Wikipedysta:AlkamidBot/listy/rodzaj/2')
	noGenderPage = pywikibot.Page(wikt, u'Wikipedysta:AlkamidBot/listy/rodzaj/wykluczone')
	
	forbidden = noGenderPage.get()
	forbiddenList = forbidden.split(u'\n')
	del forbiddenList[0]
	forbiddenList.remove('')
	for a in forbiddenList:
		a = a.strip()

	tempLangs = []
	
	notFound = []
	lenTest = u''
	text = u'Lista słów (część pierwsza), w których w sekcji "znaczenia" występuje "rzeczownik", lecz nie ma rodzaju. Dane z %s. Jeśli znajduje się tu język, w którym rzeczowniki nie mają rodzaju, dodaj go [[Wikipedysta:AlkamidBot/listy/rodzaj/wykluczone|tutaj]].\n[[Wikipedysta:AlkamidBot/listy/rodzaj/2|Część druga]].\n' % (data_slownie)
	text2 = u'Lista słów (część druga), w których w sekcji "znaczenia" występuje "rzeczownik", lecz nie ma rodzaju. Dane z %s. Jeśli znajduje się tu język, w którym rzeczowniki nie mają rodzaju, dodaj go [[Wikipedysta:AlkamidBot/listy/rodzaj/wykluczone|tutaj]].\n[[Wikipedysta:AlkamidBot/listy/rodzaj/1|Część pierwsza]]\n' % (data_slownie)
	notFoundList = collections.defaultdict(list)
	
	LangsMediaWiki = getAllLanguages()
	gwary = [u'{{poznań}}', u'{{białystok}}', u'{{częstochowa}}', u'gwara więzienna', u'{{gwara}}', u'{{góry}}', u'{{kielce}}', u'{{kraków}}', u'{{kresy}}', u'{{kujawy}}', u'{{lwów}}', u'{{mazowsze}}', u'{{reg', u'{{regionalizm', u'{{warmia}}', u'{{warszawa}}', u'{{łódź}}', u'{{śląsk}}']
	allNounsCount= {}
	for a in LangsMediaWiki:
		allNounsCount[a.shortName] = 0
	
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
								if u'rzeczownik' in d[0] and u'{{forma rzeczownika' not in d[0]:
									try: allNounsCount[u'%s' % lang.lang] += 1
									except KeyError:
										pass
									if u'rodzaj' not in d[0]:
										#gwara = 0
										#for gw in gwary:
										#	if gw in d[1]:
										#		gwara = 1
										#if not gwara and word.title[-1] != u'a' and word.title[-3:] != u'cki' and word.title[-3:] != u'ski':
										notFoundList[u'%s' % lang.lang].append(word.title)
	
	for a in LangsMediaWiki:
		if notFoundList[u'%s' % a.shortName] and a.shortName not in forbiddenList[0]:
			lenTest += u'== %s ==' % (a.longName)
			for b in notFoundList[u'%s' % a.shortName]:
				lenTest += u'\n*[[%s]]' % (b)
			lenTest += u'\n'
			
	lenHalf = len(lenTest)/2
	
	for a in LangsMediaWiki:
		if notFoundList[u'%s' % a.shortName] and a.shortName not in forbiddenList[0]:
			if len(text) < lenHalf:
				text += u'== %s ==' % (a.longName)
				text += u'\nRodzaju nie posiada \'\'\'%.1f%%\'\'\' rzeczowników' % (float(len(notFoundList[a.shortName]))/float(allNounsCount[a.shortName])*100.0)
				for b in notFoundList[u'%s' % a.shortName]:
					text += u'\n*[[%s]]' % (b)
				text += u'\n'
			else:
				text2 += u'== %s ==' % (a.longName)
				text2 += u'\nRodzaju nie posiada \'\'\'%.1f%%\'\'\' rzeczowników' % (float(len(notFoundList[a.shortName]))/float(allNounsCount[a.shortName])*100.0)
				for b in notFoundList[u'%s' % a.shortName]:
					text2 += u'\n*[[%s]]' % (b)
				text2 += u'\n'
			
	file = open('output/bez_rodzaju_1.txt', 'w')
	file.write(text.encode( "utf-8" ))
	file.close
	
	file = open('output/bez_rodzaju_2.txt', 'w')
	file.write(text2.encode( "utf-8" ))
	file.close
	
        outputPage1.text = text
        outputPage2.text = text2 

	outputPage1.save(comment=u"Aktualizacja listy", botflag=False)
	outputPage2.save(comment=u"Aktualizacja listy", botflag=False)
