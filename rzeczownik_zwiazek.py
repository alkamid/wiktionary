#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append('/home/adam/wikt/pywikipedia')
#sys.path.append('/home/alkamid/wikt/pywikipedia')
import wikipedia
import catlib
import pagegenerators
import re
import xmlreader
from klasa import *
	
def main():

	data = u'20110310'

	site = wikipedia.getSite()
	cat = catlib.Category(site,u'Kategoria:francuski (indeks)')
	lista = pagegenerators.CategorizedPageGenerator(cat)
	#lista_stron1 = xmlreader.XmlDump('plwiktionary-%s-pages-articles.xml' % data)
	
	#lista = xmlreader.XmlDump.parse(lista_stron1)	
	
	for a in lista:
		h = Haslo(a.title())
		#h = HasloXML(a.title, a.text)
		if h.type != 4 and u' ' in h.title:
			h.langs()
			for c in h.list_lang:
				c.pola()
				if c.type != 2 and c.lang == u'hiszpański':
					if (u'rzeczownik' in c.znaczenia.tresc) and (u'rzeczownika' not in c.znaczenia.tresc):
						print u'\n' + h.title
						text = u'*[[%s]]\n' % h.title
						file = open("log/rzeczownik.txt", 'a')
						file.write (text.encode("utf-8"))
						file.close
					
if __name__ == '__main__':
	try:
		main()
	finally:
		wikipedia.stopme()
