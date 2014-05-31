#!/usr/bin/python
# -*- coding: utf-8 -*-

# szuka danego przez szukany_tekst wyrażenia w hasłach

import codecs
from pywikibot import Category
import pywikibot
from pywikibot import pagegenerators
import re
from pywikibot.compat import query
from datetime import datetime
import time
from klasa import *

def main():
	
	h = Haslo(u'ucraina')
	l = h.listLangs[0]
	l.pola()
	for a in l.znaczeniaDetail:
		print a
	
	#mylist = RecentChanges('2012-02-18T16:30:00Z')
	'''
	try: h = Haslo('Benin')
	except sectionsNotFound:
		pass
	except WrongHeader:
		pass
	else:
		startTime = datetime.datetime.now()
		for elem in h.listLangs:
			elem.pola()
		print(datetime.datetime.now()-startTime)'''	
		
		
		
	'''print query.GetData(params)['query']
	
	site = pywikibot.getSite()
	lista = pagegenerators.RecentchangesPageGenerator(100, site)
	lista1 = pagegenerators.RecentchangesPageGenerator(100, site)
	
	#lista = [pywikibot.Page(site, u'depuis')]
	
	#for a in lista:
		#his = a.getVersionHistory()
		#print his[0][1]
		#rev = a.latestRevision()
		#print rev
		#print a.title()
	#print '---------------------------------------------------------------------------'
	#for b in lista1:
		#print b.title()
		try: h = Haslo(a.title())
		except sectionsNotFound:
			pass
		except WrongHeader:
			pass
		else:
			if h.type == 3:	
				print h.title'''
	
	'''
	site = pywikibot.getSite()
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
	lista_gen = []
	
	lista_stron1 = xmlreader.XmlDump('plwiktionary-20100330-pages-articles.xml')
	lista_stron = xmlreader.XmlDump.parse(lista_stron1)
	
	lista_stron2 = []
	for p in lista_stron:
		if u'Wikisłownik:' not in p.title and u'Szablon:' not in p.title and u'Kategoria:' not in p.title and u'Wikipedysta:' not in p.title and u'Aneks:' not in p.title and u'Indeks:' not in p.title and u'MediaWiki:' not in p.title and u'Portal:' not in p.title and u'Indeks:' not in p.title and u'Plik:' not in p.title and u'#PATRZ' not in p.text and u'Pomoc:' not in p.title and u'sentencja łacińska' not in p.text and u'{{przysłowie' not in p.text and u': (1.1) {{zob|' not in p.text:
			if u'{{język japoński}}' not in p.text and u'{{język polski}}' not in p.text:
			#if u'{{język francuski}}' in p.text:
				lista_stron2.append(p)
	
	sekcje_join ='|'.join(map(re.escape, sekcje))	
	szukany_tekst = re.compile(u'{{odmiana}}.*\n{{składnia}}')

	out = u''
	redir = re.compile(u'#[rR][eE][dD][iI][rR][eE][cC][tT]')
	tam = re.compile(u'#[tT][aA][mM]')
	patrz = re.compile(u'#[pP][aA][tT][rR][zZ]')
	
	for page in lista_stron2:
	
		text = page.text

		text_znajdz = re.search(u'{{źródła}}' , text)
		#if text_znajdz == None:
		
		znajdz_redir = re.search(redir, text)
		znajdz_tam = re.search(tam, text)
		znajdz_patrz = re.search(patrz, text)
		znajdz_symbol = re.search(u'\({{użycie międzynarodowe}}\) ==\n{{znaczenia}}\n\'\'symbol\'\'', text)
		
		if znajdz_redir == None and znajdz_tam == None and znajdz_patrz == None and znajdz_symbol == None:
			
			if u'{{przykłady}}' not in text:
				#print '*[[' + page.title + ']]'
				#out = out + '*[[' + page.title + ']]\n'
				lista_gen.append(u'%s' % (page.title))
	
	for pp in lista_gen:
		
		page = pywikibot.Page(site, u'%s' % (pp))
		try:
			text = page.get()
		except pywikibot.NoPage:
			continue
		except pywikibot.IsRedirectPage:
			continue
		except pywikibot.Error:
			print 'nieznany błąd'
		
		if u'{{przykłady}}' not in text:
			print '*[[' + page.title() + ']]'
			out = out + '*[[' + page.title() + ']]\n'
			
	filename = "output-sprzątanie.txt"

	file = open(filename, 'w')
	file.write(out.encode( "utf-8" ))
	file.close'''
	
if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
