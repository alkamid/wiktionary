#!/usr/bin/python
# -*- coding: utf-8 -*-

# do eksportowania wszystkich słów z podanych języków

import sys
sys.path.append('/home/adam/pywiki/pywikipedia')
import codecs
import catlib
import wikipedia
import pagegenerators
import re

def dodaj_jezyk(lang):
	
	if (lang == 'interlingua' or lang == 'jidysz' or lang == 'ido' or lang == 'esperanto'  or lang == 'slovio' or lang == 'tetum' or lang == 'hindi'):
		short = lang		
	else:
		short = u'język %s' % (lang)
	site = wikipedia.getSite()
	cat = catlib.Category(site,u'Kategoria:%s_(indeks)' % (lang))
	lista_stron = pagegenerators.CategorizedPageGenerator(cat)

	text = u''
	for page in lista_stron:
		try:
			exists = page.title()
		except wikipedia.NoPage:
			print u'strona nie istnieje'
		except wikipedia.IsRedirectPage:
			print u'%s - przekierowanie' % (page.title())
		except wikipedia.Error:
			print u'nieznany błąd'
	
		text = text + u'\n%s' % exists

	filename = "outputexport.txt"

	file = open(filename, 'a')
	file.write(text.encode( "utf-8" ))
	file.close
	
	
def main():
	jezyki = []
	
	jezyki.append([u'słoweński'])
	jezyki.append([u'afrykanerski'])
	jezyki.append([u'chiński standardowy'])
	jezyki.append([u'macedoński'])
	jezyki.append([u'hawajski'])
	jezyki.append([u'serbski'])
	jezyki.append([u'słowacki'])
	jezyki.append([u'łotewski'])
	jezyki.append([u'górnołużycki'])
	jezyki.append([u'turecki'])
	jezyki.append([u'rumuński'])
	jezyki.append([u'sycylijski'])
	jezyki.append([u'holenderski'])
	jezyki.append([u'hindi'])
	jezyki.append([u'tetum'])
	jezyki.append([u'kaszubski'])
	jezyki.append([u'ido'])
	jezyki.append([u'arabski'])
	jezyki.append([u'gruziński'])
	jezyki.append([u'litewski'])
	jezyki.append([u'dolnołużycki'])
	jezyki.append([u'fiński'])
	jezyki.append([u'hebrajski'])
	jezyki.append([u'chorwacki'])
	jezyki.append([u'koreański'])
	jezyki.append([u'portugalski'])
	jezyki.append([u'suahili'])
	jezyki.append([u'białoruski'])
	jezyki.append([u'bułgarski'])
	jezyki.append([u'duński'])
	jezyki.append([u'łaciński'])
	jezyki.append([u'węgierski'])
	jezyki.append([u'ukraiński'])
	jezyki.append([u'norweski (bokmål)'])
	jezyki.append([u'islandzki'])
	jezyki.append([u'grecki'])
	jezyki.append([u'slovio'])
	jezyki.append([u'japoński'])
	jezyki.append([u'esperanto'])
	jezyki.append([u'niemiecki'])
	jezyki.append([u'rosyjski'])
	jezyki.append([u'hiszpański'])
	jezyki.append([u'włoski'])
	jezyki.append([u'jidysz'])
	jezyki.append([u'czeski'])
	jezyki.append([u'szwedzki'])
	jezyki.append([u'interlingua'])
	jezyki.append([u'francuski'])
	jezyki.append([u'angielski'])
	jezyki.append([u'polski'])
	
	for lang in jezyki:
		dodaj_jezyk(lang[0])
if __name__ == '__main__':
    try:
        main()
    finally:
        wikipedia.stopme()
