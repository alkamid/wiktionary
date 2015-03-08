#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators
import re
from pywikibot import xmlreader
import collections
from klasa import *
	
def brakCzesciMowy(data):

	data_slownie = data[6] + data[7] + u'.' + data[4] + data[5] + u'.' + data[0] + data[1] + data[2] + data[3]
	lista_stron = getListFromXML(data)
	wikt = pywikibot.Site('pl', 'wiktionary')
	outputPage = pywikibot.Page(wikt, u'Wikipedysta:AlkamidBot/listy/części_mowy')
	
	tempLangs = []
	
	notFound = []
	text = u'Do poniższych haseł nie wpisano, jakimi są częściami mowy - jeśli potrafisz, zrób to. Ostatnia aktualizacja wg zrzutu bazy danych z %s.\n' % (data_slownie)
	notFoundList = collections.defaultdict(list)
	
	LangsMediaWiki = getAllLanguages()

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
							notFoundList[u'%s' % lang.lang].append(lang.title)
													
	for a in LangsMediaWiki:
		if notFoundList[u'%s' % a.shortName]:
			text += u'== %s ==' % (a.longName)
			for b in notFoundList[u'%s' % a.shortName]:
				text += u'\n*[[%s]]' % (b)
			text += u'\n'

	file = open('output/bez_części_mowy.txt', 'w')
	file.write(text.encode( "utf-8" ))
	file.close
	
        outputPage.text = text
	outputPage.save(comment=u"Aktualizacja listy", botflag=False)
