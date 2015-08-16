#!/usr/bin/python
# -*- coding: utf-8 -*-

# szuka danego przez szukany_tekst wyrażenia w hasłach

import subprocess
import sys
sys.path.append('/home/adam/pywiki/pywikipedia')
import codecs
from pywikibot import Category
import pywikibot
from pywikibot import pagegenerators
import re
from pywikibot import xmlreader

def main():
	
	sekcje = []
	sekcje.append('{{odmiana')
	sekcje.append('{{etymologia}}')
	sekcje.append('{{wymowa}}')
	sekcje.append('{{znaczenia}}')
	sekcje.append('{{przykłady}}')
	sekcje.append('{{składnia}}')
	sekcje.append('{{kolokacje}}')
	sekcje.append('{{pokrewne}}')
	sekcje.append('{{frazeologia}}')
	sekcje.append('{{uwagi}}')
	sekcje.append('{{synonimy}}')
	sekcje.append('{{antonimy}}')
	sekcje.append('{{źródła}}')
	
	site = pywikibot.getSite()
	cat = Category(site,'Kategoria:łaciński (indeks)')
	lista_stron = pagegenerators.CategorizedPageGenerator(cat)
	#lista_stron = pagegenerators.AllpagesPageGenerator(namespace = 0, includeredirects = False)
	
	'''lista_stron2 = []
	for p in lista_stron:
		if u'Wikisłownik:' not in p.title and u'Szablon:' not in p.title and u'Kategoria:' not in p.title and u'Wikipedysta:' not in p.title and u'Aneks:' not in p.title and u'Indeks:' not in p.title and u'MediaWiki:' not in p.title and u'Portal:' not in p.title and u'Indeks:' not in p.title and u'#TAM' not in p.text and u'#PATRZ' not in p.text and u'Pomoc:' not in p.title and u'#REDIRECT' not in p.text and u'sentencja łacińska' not in p.text and u'#patrz' not in p.text and u'#tam' not in p.text:
			#if u'{{język francuski}}' in p.text:
			lista_stron2.append(p)
	
	sekcje_join ='|'.join(map(re.escape, sekcje))	
	szukany_tekst = re.compile(u'{{odmiana}}.*\n{{składnia}}')
	'''
	out = ''
	
	for page in lista_stron:
	
		text = page.get()

		if '{{przykłady}}' not in text:
			print('*[[' + page.title() + ']]')
			out = out + '*[[' + page.title() + ']]\n'
			
			
	filename = "output-sprzątanie.txt"

	file = open(filename, 'w')
	file.write(out.encode( "utf-8" ))
	file.close
	
if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
