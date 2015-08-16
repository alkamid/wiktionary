#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators
import re
from pywikibot import xmlreader
import collections
from klasa import *
from statystykanowa import refs
	
def main():

	data = '20110723'
	data_slownie = data[6] + data[7] + '.' + data[4] + data[5] + '.' + data[0] + data[1] + data[2] + data[3]
	lista_stron1 = xmlreader.XmlDump('/mnt/user-store/dumps/plwiktionary/plwiktionary-%s-pages-articles.xml' % data)
	lista_stron = xmlreader.XmlDump.parse(lista_stron1)
	wikt = pywikibot.Site('pl', 'wiktionary')
	outputPage = pywikibot.Page(wikt, 'Wikipedysta:AlkamidBot/listy/bez_źródła')
	
	notFoundList = collections.defaultdict(list)
	
	for a in lista_stron:
		try: word = Haslo(a.title, a.text)
		except notFromMainNamespace:
			pass
		except sectionsNotFound:
			pass
		else:
			if word.type == 3:
				for lang in word.listLangs:
					if lang.type != 2 and lang.lang == 'arabski':
						lang.pola()
						if lang.type == 1:
							if not refs(lang.content, lang.zrodla):
								notFoundList['arabski'].append(lang.title)
	
	text = ''												
	for a in notFoundList:
		text += '== %s ==' % (a)
		for b in notFoundList[a]:
			text += '\n*[[%s]]' % (b)
		text += '\n'

	file = open('output/bez_zrodla.txt', 'w')
	file.write(text.encode( "utf-8" ))
	file.close
	
	outputPage.put(text, comment="Aktualizacja listy")

if __name__ == '__main__':
	try:
		main()
	finally:
		pywikibot.stopme()


