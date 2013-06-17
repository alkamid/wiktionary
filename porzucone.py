#!/usr/bin/python
# -*- coding: utf-8 -*-

# robienie listy haseł polskich bez wymowy

import codecs
import catlib
import wikipedia
import pagegenerators
import re
import math
import datetime

def main():
	
	site = wikipedia.getSite()
	
	cat_main = catlib.Category(site,u'Kategoria:polski (indeks)')
	cat_gwary = catlib.Category(site, u'Kategoria:Polski_(dialekty_i_gwary)')

	output_main = wikipedia.Page(site, u'Wikipedysta:AlkamidBot/porzucone')
	
	lista_main = pagegenerators.CategorizedPageGenerator(cat_main)
	lista_gwary = pagegenerators.CategorizedPageGenerator(cat_gwary, recurse=True)
	
	lista = []
	lista_gwary1 = []
	lista_gwary2 = []
	count_all = 0
	final = u'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n<html xmlns="http://www.w3.org/1999/xhtml\nxml:lang="pl">\n<head>\n<meta http-equiv="content-type" content="text/html; charset=UTF-8" />\n</head><body>'
	final = final + u'Poniżej znajduje się lista polskich haseł, do których nie linkuje nic oprócz stron z przestrzeni nazw Wikipedysta. Z związku z tym trudno trafić do takiego hasła inaczej niż przez bezpośrednie jego wyszukanie. Jeśli możesz - dodaj w innym haśle odnośnik do porzuconego słowa, np. w przykładach lub pokrewnych. '
	final_lista = u''
	
	wikipedysta = pagegenerators.AllpagesPageGenerator(namespace=2)
	
	wykluczone = []
	for a in wikipedysta:
		wykluczone.append(a)

	for page in lista_main:
		if page not in lista_gwary:
			try:
				strona = wikipedia.Page(site, page.title())
			except wikipedia.Error:
				print u'error'
			else:
				pages = [a for a in strona.getReferences()]
				for b in wykluczone:
					if b in pages:
						pages.remove(b)
				if strona in pages:
					pages.remove(strona)
				if not pages:
					dodaj = u'\n<br /><a href="http://pl.wiktionary.org/wiki/%s">%s</a>' % (strona.title(), strona.title())
					final_lista = final_lista + dodaj
					count_all = count_all + 1
					

	data = datetime.datetime.now() + datetime.timedelta(hours=2)
	data1 = data.strftime("Ostatnia aktualizacja listy: %Y-%m-%d, %H:%M:%S")
	
	final = final + data1 + u'<br />: Licznik porzuconych: %d' % count_all
	final = final + final_lista
	final = final + u'</body></html>'
		
	file = open('/home/alkamid/public_html/porzucone.html', 'w')
	file.write(final.encode( "utf-8" ))
	file.close

if __name__ == '__main__':
    try:
        main()
    finally:
        wikipedia.stopme()
