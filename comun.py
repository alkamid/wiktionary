#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import Category
from pywikibot import pagegenerators
import re
from pywikibot import xmlreader
from klasa import *
	
def main():

	data = '20110617'
	lista_stron1 = xmlreader.XmlDump('/mnt/user-store/dumps/plwiktionary/plwiktionary-%s-pages-articles.xml' % data)
	lista_stron = xmlreader.XmlDump.parse(lista_stron1)
	
	for a in lista_stron:
		h = Haslo(a.title, a.text)
		if h.type == 3:
			h.langs()
			for c in h.listLangs:
				c.pola()
				if c.type != 2 and c.lang == u'hiszpański':
					if u'męski lub żeński' in c.znaczeniaWhole.tresc:
						print u'\n' + h.title
						text = u'*[[%s]]\n' % h.title
						file = open("log/comun.txt", 'a')
						file.write (text.encode("utf-8"))
						file.close
					
if __name__ == '__main__':
	try:
		main()
	finally:
		pywikibot.stopme()

