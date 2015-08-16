#!/usr/bin/python
# -*- coding: utf-8 -*-

# frekwencja - tworzy zwikilinkowaną listę danej części mowy (linijka 27) z listy z francuskiego słownika frekwencyjnego

import sys
sys.path.append('/home/adam/pywiki/pywikipedia')
import codecs
import pywikibot

def main():
	site = pywikibot.getSite()
	lista = []
	inp = codecs.open('myfile', encoding='utf-8')

	for line in inp:
		lista.append(line.split())
	
	def sortkey(row):
		return int(row[-1])
	
	lista.sort(key=sortkey, reverse=True)

	text = ''
	i=0.00
	for a in lista:
		if (a[1] == "v"):
			
			page = pywikibot.Page(site, '%s' % (a[0]))
			try:
				exists = page.get()
			except pywikibot.NoPage:
				text += '*[[' + a[0] + '#fr|' + a[0] + ']]' + '\n'
			except pywikibot.IsRedirectPage:
				text += '*[[' + a[0] + '#fr|' + a[0] + ']] - przekierowanie' + '\n'
			except pywikibot.Error:
				print('nieznany błąd')
		
			i+=1.00
			print('%.2f' % (i/50)) 
	
	filename = "outputverbes.txt"

	file = open(filename, 'w')
	file.write(text.encode( "utf-8" ))
	file.close
	
if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
