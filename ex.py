#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
#sys.path.append('/home/adam/wikt/pywikipedia')
sys.path.append('/home/alkamid/wikt/pywikipedia')
import pywikibot
from pywikibot import Category
from pywikibot import pagegenerators
import re
from klasa import *
	
def main():

	site = pywikibot.getSite()
	cat = Category(site,u'Kategoria:francuski (indeks)')
	lista = pagegenerators.CategorizedPageGenerator(cat)
	
	
	for a in lista:
		h = Haslo(a.title())
		if h.typ == 3:
			h.sekcje()
			for c in h.lista_sekcje:
				if u'francuski' in c.jezyk:
					print u'\n' + h.tytul
					c.pola()
					print c.przyklady.tresc
					if (c.przyklady.tresc == u'\n: (1.1)' or c.przyklady.tresc == u'\n: (1.1) ') and (u'rzeczownik' not in c.znaczenia.tresc) and (u'{{forma czasownika|fr}}' not in c.znaczenia.tresc):
						text = u'*[[%s]]\n' % h.tytul
						file = open("log/ex.txt", 'a')
						file.write (text.encode("utf-8"))
						file.close

if __name__ == '__main__':
	try:
		main()
	finally:
		pywikibot.stopme()
