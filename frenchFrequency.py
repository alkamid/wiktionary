#!/usr/bin/python
# -*- coding: utf-8 -*-

# missing French words, based on the frequency list from http://corpus.leeds.ac.uk/frqc/internet-fr.num

import codecs
import pywikibot
import datetime
import re
import config
import urllib2
from klasa import *

def main():
	site = pywikibot.Site()
	outputPage = pywikibot.Page(site, u'Portal:Francuski/potrzebne')
        excludedPage = pywikibot.Page(site, u'Portal:Francuski/potrzebne/wykluczone')
	excludedList = excludedPage.get().split('\n')
	date = datetime.datetime.now().strftime("%Y-%m-%d")

        inp = codecs.open('%sinne/lista_franc.txt' % config.path['scripts'], encoding='utf-8')

        wordList = [line.split()[2].split('|')[0] for line in inp]

	re_stary = re.compile(u'(\*.*?\n)\[\[Kat', re.DOTALL)

        text = u''
	counter = 0
	
        startPoint = 310 #all the words < 300 already exist, no point checking there

	for word in wordList[startPoint:]:

                if word not in excludedList and len(word)>1:
			try:
				haslo = Haslo(word)
			except urllib2.HTTPError:
				pass
			except sectionsNotFound:
				pass
			except WrongHeader:
				text += u'*[[' + word + ']] - problem z nagłówkiem' + '\n'
			else:
				if haslo.type == 0:
					text += u'*[[' + word + ']] - przekierowanie' + '\n'
				elif haslo.type == 1:
					text += u'*[[' + word + ']]' + '\n'
					counter += 1
				elif haslo.type == 2:
					print u'*--------* nieznany błąd (haslo.type=2) *----------------*'
				else:
					found = 0
					try: haslo.listLangs
					except AttributeError:
						pass
					else:
						for section in haslo.listLangs:
							if section.lang == u'francuski':
								found = 1
						if not found:
							text += u'*[[' + word + ']]' + '\n'
							counter += 1
		
			if counter == 100:
				stary_s = re.search(re_stary, outputPage.get())
				if (stary_s.group(1) != text):
					final = u'{{język linków|francuski}}\nOto lista około stu najczęściej występujących haseł w języku francuskim, których nie ma jeszcze na Wikisłowniku. Jeśli możesz - dodaj je. Lista ta jest wyborem słów z zestawienia stworzonego przez [http://corpus.leeds.ac.uk/list.html korpus University of Leeds].\nOstatnia aktualizacja: %s\n%s[[Kategoria:Listy frekwencyjne|francuski]]' % (date, text)
					outputPage.put(final, comment=u'Aktualizacja listy')
				return 0
	
	
if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
