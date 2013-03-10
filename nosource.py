#!/usr/bin/python
# -*- coding: utf-8 -*-

import wikipedia
import pagegenerators
import re
import xmlreader
import collections
from klasa import *
from statystykanowa import refs
	
def main():

	data = '20110723'
	data_slownie = data[6] + data[7] + u'.' + data[4] + data[5] + u'.' + data[0] + data[1] + data[2] + data[3]
	lista_stron1 = xmlreader.XmlDump('/mnt/user-store/dumps/plwiktionary/plwiktionary-%s-pages-articles.xml' % data)
	lista_stron = xmlreader.XmlDump.parse(lista_stron1)
	wikt = wikipedia.Site('pl', 'wiktionary')
	outputPage = wikipedia.Page(wikt, u'Wikipedysta:AlkamidBot/listy/bez_źródła')
	
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
					if lang.type != 2 and lang.lang == u'arabski':
						lang.pola()
						if lang.type == 1:
							if not refs(lang.content, lang.zrodla):
								notFoundList[u'arabski'].append(lang.title)
	
	text = u''												
	for a in notFoundList:
		text += u'== %s ==' % (a)
		for b in notFoundList[a]:
			text += u'\n*[[%s]]' % (b)
		text += u'\n'

	file = open('output/bez_zrodla.txt', 'w')
	file.write(text.encode( "utf-8" ))
	file.close
	
	outputPage.put(text, comment=u"Aktualizacja listy")

if __name__ == '__main__':
	try:
		main()
	finally:
		wikipedia.stopme()


