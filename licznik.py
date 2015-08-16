#!/usr/bin/python
# -*- coding: utf-8 -*-

# licznik multimediów w hasłach

import sys
sys.path.append('/home/adam/pywiki/pywikipedia')
import codecs
from pywikibot import Category
import pywikibot
from pywikibot import pagegenerators
from pywikibot import xmlreader
import re
import math

def main():
	
	site = pywikibot.getSite()
	lista_stron1 = xmlreader.XmlDump('plwiktionary-20100922-pages-articles.xml')
	lista_stron = xmlreader.XmlDump.parse(lista_stron1)
	dlaczego_strona = pywikibot.Page(site, 'Wikisłownik:Dlaczego Wikisłownik')
	liczba_znakow = 0.0
	liczba_slow = 0.0
	liczba_audio = 0
	liczba_grafik = 0
	
	audio = re.compile('{{audio.*?}}')
	grafika = []
	grafika.append('\[\[Grafika:.*?\]\]')
	grafika.append('\[\[Image:.*?\]\]')
	grafika.append('\[\[Media:.*?\]\]')
	grafika.append('\[\[File:.*?\]\]')
	grafika.append('\[\[Plik:.*?\]\]')
	dlaczego_przed = re.compile('(.*=== Multimedia ===\n\[\[Plik\:Crystal Clear app voice\-support\.png\|right\|100px\]\]\n\* na Wikisłowniku znajdziesz ponad \'\'\')', re.DOTALL)
	dlaczego_po = re.compile('(\), które ułatwiają zapamiętywanie nowych słów oraz pokazują to, co często ciężko opisać słowami.*)', re.DOTALL)
	dlaczego_proc = re.compile('\* plik z wymową posiada(.*?)% angielskich')
	
	grafika_join = '|'.join(map(re.escape,grafika))
	
	for page in lista_stron:

		try:
			text = page.text
		except pywikibot.NoPage:
			print('strona nie istnieje')
		except pywikibot.IsRedirectPage:
			print('%s - przekierowanie' % (page.title()))
		except pywikibot.Error:
			print('nieznany błąd')
			
		liczba_audio += len(re.findall(audio, text))
		liczba_grafik += len(re.findall('\[\[(\s*|)((P|p)lik|(F|f)ile|(M|m)edia|(I|i)mage|(G|g)rafika)(\s*|):', text))

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
	
	
	tekst = ''
	if dlaczego_przed_s != None and dlaczego_po_s != None and dlaczego_proc_s:
		tekst = dlaczego_przed_s.group(1)
		tekst = tekst + '%d' % liczba_audio
		tekst = tekst + ' nagrań wymowy\'\'\' w wielu językach (na przykład w [[solder|angielskim]], [[акация|rosyjskim]], [[können|niemieckim]] czy [[trzydzieści|polskim]]) wykonanych przez osoby używające danego języka jako ojczystego. To jedyny taki słownik w Internecie!\n* plik z wymową posiada'
		tekst = tekst + dlaczego_proc_s.group(1)
		tekst = tekst + '% angielskich\n* nagrania można ściągnąć na dysk lub [[:Grafika:En-uk-ubiquitous.ogg|odsłuchać w przeglądarce]]\n* Wikisłownik to słownik multimedialny &mdash; w hasłach znajdziesz \'\'\'ilustracje\'\'\' (ponad '
		tekst = tekst + '%d' % liczba_grafik
		tekst = tekst + dlaczego_po_s.group(1)
	else:
		print('coś poszło nie tak\n')
		
	dlaczego_strona.put(tekst, comment = 'Aktualizacja z ostatniego zrzutu bazy danych', botflag=False)

if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
