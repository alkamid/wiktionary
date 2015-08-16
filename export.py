#!/usr/bin/python
# -*- coding: utf-8 -*-

# do eksportowania wszystkich słów z podanych języków

import sys
sys.path.append('/home/adam/pywiki/pywikipedia')
import codecs
from pywikibot import Category
import pywikibot
from pywikibot import pagegenerators
import re

def dodaj_jezyk(lang):
	
	if (lang == 'interlingua' or lang == 'jidysz' or lang == 'ido' or lang == 'esperanto'  or lang == 'slovio' or lang == 'tetum' or lang == 'hindi'):
		short = lang		
	else:
		short = 'język %s' % (lang)
	site = pywikibot.getSite()
	cat = Category(site,'Kategoria:%s_(indeks)' % (lang))
	lista_stron = pagegenerators.CategorizedPageGenerator(cat)

	text = ''
	for page in lista_stron:
		try:
			exists = page.title()
		except pywikibot.NoPage:
			print('strona nie istnieje')
		except pywikibot.IsRedirectPage:
			print('%s - przekierowanie' % (page.title()))
		except pywikibot.Error:
			print('nieznany błąd')
	
		text = text + '\n%s' % exists

	filename = "outputexport.txt"

	file = open(filename, 'a')
	file.write(text.encode( "utf-8" ))
	file.close
	
	
def main():
	jezyki = []
	
	jezyki.append(['słoweński'])
	jezyki.append(['afrykanerski'])
	jezyki.append(['chiński standardowy'])
	jezyki.append(['macedoński'])
	jezyki.append(['hawajski'])
	jezyki.append(['serbski'])
	jezyki.append(['słowacki'])
	jezyki.append(['łotewski'])
	jezyki.append(['górnołużycki'])
	jezyki.append(['turecki'])
	jezyki.append(['rumuński'])
	jezyki.append(['sycylijski'])
	jezyki.append(['holenderski'])
	jezyki.append(['hindi'])
	jezyki.append(['tetum'])
	jezyki.append(['kaszubski'])
	jezyki.append(['ido'])
	jezyki.append(['arabski'])
	jezyki.append(['gruziński'])
	jezyki.append(['litewski'])
	jezyki.append(['dolnołużycki'])
	jezyki.append(['fiński'])
	jezyki.append(['hebrajski'])
	jezyki.append(['chorwacki'])
	jezyki.append(['koreański'])
	jezyki.append(['portugalski'])
	jezyki.append(['suahili'])
	jezyki.append(['białoruski'])
	jezyki.append(['bułgarski'])
	jezyki.append(['duński'])
	jezyki.append(['łaciński'])
	jezyki.append(['węgierski'])
	jezyki.append(['ukraiński'])
	jezyki.append(['norweski (bokmål)'])
	jezyki.append(['islandzki'])
	jezyki.append(['grecki'])
	jezyki.append(['slovio'])
	jezyki.append(['japoński'])
	jezyki.append(['esperanto'])
	jezyki.append(['niemiecki'])
	jezyki.append(['rosyjski'])
	jezyki.append(['hiszpański'])
	jezyki.append(['włoski'])
	jezyki.append(['jidysz'])
	jezyki.append(['czeski'])
	jezyki.append(['szwedzki'])
	jezyki.append(['interlingua'])
	jezyki.append(['francuski'])
	jezyki.append(['angielski'])
	jezyki.append(['polski'])
	
	for lang in jezyki:
		dodaj_jezyk(lang[0])
if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
