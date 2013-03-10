#!/usr/bin/python
# -*- coding: utf-8 -*-

# licznik multimediów w hasłach

import sys
sys.path.append('/home/adam/pywiki/pywikipedia')
import codecs
import catlib
import wikipedia
import pagegenerators
import xmlreader
import re
import math

def main():
	
	site = wikipedia.getSite()
	lista_stron1 = xmlreader.XmlDump('plwiktionary-20100922-pages-articles.xml')
	lista_stron = xmlreader.XmlDump.parse(lista_stron1)
	dlaczego_strona = wikipedia.Page(site, u'Wikisłownik:Dlaczego Wikisłownik')
	liczba_znakow = 0.0
	liczba_slow = 0.0
	liczba_audio = 0
	liczba_grafik = 0
	
	audio = re.compile(u'{{audio.*?}}')
	grafika = []
	grafika.append(u'\[\[Grafika:.*?\]\]')
	grafika.append(u'\[\[Image:.*?\]\]')
	grafika.append(u'\[\[Media:.*?\]\]')
	grafika.append(u'\[\[File:.*?\]\]')
	grafika.append(u'\[\[Plik:.*?\]\]')
	dlaczego_przed = re.compile(u'(.*=== Multimedia ===\n\[\[Plik\:Crystal Clear app voice\-support\.png\|right\|100px\]\]\n\* na Wikisłowniku znajdziesz ponad \'\'\')', re.DOTALL)
	dlaczego_po = re.compile(u'(\), które ułatwiają zapamiętywanie nowych słów oraz pokazują to, co często ciężko opisać słowami.*)', re.DOTALL)
	dlaczego_proc = re.compile(u'\* plik z wymową posiada(.*?)% angielskich')
	
	grafika_join = '|'.join(map(re.escape,grafika))
	
	for page in lista_stron:

		try:
			text = page.text
		except wikipedia.NoPage:
			print u'strona nie istnieje'
		except wikipedia.IsRedirectPage:
			print u'%s - przekierowanie' % (page.title())
		except wikipedia.Error:
			print u'nieznany błąd'
			
		liczba_audio += len(re.findall(audio, text))
		liczba_grafik += len(re.findall(u'\[\[(\s*|)((P|p)lik|(F|f)ile|(M|m)edia|(I|i)mage|(G|g)rafika)(\s*|):', text))

	dodaj = "audio: %d, grafiki: %d" % (liczba_audio, liczba_grafik)
	
	dlaczego_przed_s = re.search(dlaczego_przed, dlaczego_strona.get())
	dlaczego_po_s = re.search(dlaczego_po, dlaczego_strona.get())
	dlaczego_proc_s = re.search(dlaczego_proc, dlaczego_strona.get())
	
	liczba_audio = liczba_audio/100
	liczba_audio = math.floor(liczba_audio)
	liczba_audio = liczba_audio*100
	liczba_grafik = liczba_grafik/100
	liczba_grafik = math.floor(liczba_grafik)
	liczba_grafik = liczba_grafik*100
	
	
	tekst = u''
	if dlaczego_przed_s != None and dlaczego_po_s != None and dlaczego_proc_s:
		tekst = dlaczego_przed_s.group(1)
		tekst = tekst + u'%d' % liczba_audio
		tekst = tekst + u' nagrań wymowy\'\'\' w wielu językach (na przykład w [[solder|angielskim]], [[акация|rosyjskim]], [[können|niemieckim]] czy [[trzydzieści|polskim]]) wykonanych przez osoby używające danego języka jako ojczystego. To jedyny taki słownik w Internecie!\n* plik z wymową posiada'
		tekst = tekst + dlaczego_proc_s.group(1)
		tekst = tekst + u'% angielskich\n* nagrania można ściągnąć na dysk lub [[:Grafika:En-uk-ubiquitous.ogg|odsłuchać w przeglądarce]]\n* Wikisłownik to słownik multimedialny &mdash; w hasłach znajdziesz \'\'\'ilustracje\'\'\' (ponad '
		tekst = tekst + u'%d' % liczba_grafik
		tekst = tekst + dlaczego_po_s.group(1)
	else:
		print u'coś poszło nie tak\n'
		
	dlaczego_strona.put(tekst, comment = u'Aktualizacja z ostatniego zrzutu bazy danych', botflag=False)

if __name__ == '__main__':
    try:
        main()
    finally:
        wikipedia.stopme()
