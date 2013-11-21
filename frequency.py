#!/usr/bin/python
# -*- coding: utf-8 -*-

# frekwencja - tworzy listę na podstawie tej z angielskiego uniwersytetu

import os
import codecs
import pywikibot
import datetime
import re
import config
from klasa import *

def main():
	site = pywikibot.getSite()
	page_list = pywikibot.Page(site, u'Portal:Francuski/potrzebne')
	lista = []
	inp = codecs.open('%sinne/lista_franc.txt' % config.path['scripts'], encoding='utf-8')
	data = datetime.datetime.now().strftime("%Y-%m-%d")

	re_stary = re.compile(u'(\*.*?\n)\[\[Kat', re.DOTALL)

	for line in inp:
		lista.append(line.split())
	
	text = ''
	licz = 0
	excluded = []
	excluded.append(u'france')
	excluded.append(u'parce')
	
	for a in lista:
		
		if a[2] not in excluded:
			try:
				haslo = Haslo(a[2])
			except urllib2.HTTPError:
				pass
			except sectionsNotFound:
				pass
			except WrongHeader:
				text += '*[[' + a[2] + ']] - problem z nagłówkiem' + '\n'
			else:
				if haslo.type == 0:
					text += '*[[' + a[2] + ']] - przekierowanie' + '\n'
				elif haslo.type == 1:
					text += '*[[' + a[2] + ']]' + '\n'
					licz = licz + 1
				elif haslo.type == 2:
					print 'nieznany błąd'
				else:

					found = 0
					try: haslo.listLangs
					except AttributeError:
						pass
					else:
						for sekcja in haslo.listLangs:
							if sekcja.lang == u'francuski':
								found = 1
						if not found:
							text += '*[[' + a[2] + ']]' + '\n'
							licz = licz + 1
		
			if licz == 100:
				stary_s = re.search(re_stary, page_list.get())
				if (stary_s.group(1) != text):
					final = u'{{język linków|francuski}}\nOto lista około stu najczęściej występujących haseł w języku francuskim, których nie ma jeszcze na Wikisłowniku. Jeśli możesz - dodaj je. Lista ta jest wyborem słów z zestawienia stworzonego przez [http://corpus.leeds.ac.uk/list.html korpus University of Leeds].\nOstatnia aktualizacja: %s\n%s[[Kategoria:Listy frekwencyjne|francuski]]' % (data, text)
					page_list.put(final, comment=u'Aktualizacja listy')
				return 0
	
	
if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
