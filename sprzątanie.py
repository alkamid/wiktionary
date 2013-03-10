#!/usr/bin/python
# -*- coding: utf-8 -*-

# szuka danego przez szukany_tekst wyrażenia w hasłach

import subprocess
import sys
sys.path.append('/home/adam/pywiki/pywikipedia')
import codecs
import catlib
import wikipedia
import pagegenerators
import re
import xmlreader

def main():
	
	sekcje = []
	sekcje.append(u'{{odmiana')
	sekcje.append(u'{{etymologia}}')
	sekcje.append(u'{{wymowa}}')
	sekcje.append(u'{{znaczenia}}')
	sekcje.append(u'{{przykłady}}')
	sekcje.append(u'{{składnia}}')
	sekcje.append(u'{{kolokacje}}')
	sekcje.append(u'{{pokrewne}}')
	sekcje.append(u'{{frazeologia}}')
	sekcje.append(u'{{uwagi}}')
	sekcje.append(u'{{synonimy}}')
	sekcje.append(u'{{antonimy}}')
	sekcje.append(u'{{źródła}}')
	
	site = wikipedia.getSite()
	cat = catlib.Category(site,u'Kategoria:łaciński (indeks)')
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
	out = u''
	
	for page in lista_stron:
	
		text = page.get()

		if u'{{przykłady}}' not in text:
			print '*[[' + page.title() + ']]'
			out = out + '*[[' + page.title() + ']]\n'
			
			
	filename = "output-sprzątanie.txt"

	file = open(filename, 'w')
	file.write(out.encode( "utf-8" ))
	file.close
	
if __name__ == '__main__':
    try:
        main()
    finally:
        wikipedia.stopme()
