#!/usr/bin/python
# -*- coding: utf-8 -*-

# robienie listy haseł polskich bez wymowy

import sys
#sys.path.append('/home/alkamid/wikt/pywikipedia')
sys.path.append('/home/adam/wikt/pywikipedia')
import codecs
import catlib
import wikipedia
import pagegenerators
import re
import math
import datetime
import xmlreader

def main():
	
	lista_stron1 = xmlreader.XmlDump('plwiktionary-20101011-pages-articles.xml')
	lista_stron2 = xmlreader.XmlDump.parse(lista_stron1)
	licz_ipa = 0
	licz_puste = 0
	licz_all = 0
	lista = []
	
	sekcja = re.compile(u'==\s*.*?\({{język francuski}}\)\s*?==((.*?)==|(.*))', re.DOTALL)
	ipa = re.compile(u'({{etym\||{{etymn\||{{etymn2\|)')
	
	for a in lista_stron2:
		if u'{{język francuski}}' in a.text:
			lista.append(a)
	
	for a in lista:
		s_sekcja = re.search(sekcja, a.text)
		if s_sekcja:
			
			tekst = s_sekcja.group(1)
			s_ipa = re.search(ipa, tekst)
			if s_ipa:
				licz_ipa = licz_ipa + 1
			else:
				print a.title
				licz_puste = licz_puste + 1
		licz_all = licz_all + 1
		
	print u'bez ipa: %d\nz ipa: %d\nwszystkie: %d' % (licz_puste, licz_ipa, licz_all)
	

if __name__ == '__main__':
    try:
        main()
    finally:
        wikipedia.stopme()
