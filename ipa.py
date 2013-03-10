#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append('/home/adam/wikt/pywikipedia')
#sys.path.append('/home/alkamid/wikt/pywikipedia')
import wikipedia
import catlib
import pagegenerators
import re
from klasa import *
	
def main():

	site = wikipedia.getSite()
	cat = catlib.Category(site,u'Kategoria:francuski (indeks)')
	lista = pagegenerators.CategorizedPageGenerator(cat, start=u'tænia')
	
	for a in lista:
		h = Haslo(a.title())
		if h.typ == 3:
			h.sekcje()
			for c in h.lista_sekcje:
				if u'francuski' in c.jezyk:
					print u'\n' + h.tytul
					c.pola()
					print c.wymowa.tresc

if __name__ == '__main__':
	try:
		main()
	finally:
		wikipedia.stopme()
