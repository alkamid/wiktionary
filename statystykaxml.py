#!/usr/bin/python
# -*- coding: utf-8 -*-

# statystyka długości haseł - pobiera ja z xml

import codecs
import catlib
import wikipedia
import pagegenerators
import re
import xmlreader
import math
from klasa import *

def licz_jezyk(lang):
	
	short = lang.longName
	print short
	
	re_lang = re.compile(u'\(\{\{%s(\|.*?\}\}\)|\}\}\))' % re.escape(short))
	
	#lista_stron1 = xmlreader.XmlDump('plwiktionary-%s-pages-articles.xml' % data)
	lista_stron1 = xmlreader.XmlDump('/mnt/user-store/dumps/plwiktionary/plwiktionary-%s-pages-articles.xml' % data)
	
	lista_stron2 = xmlreader.XmlDump.parse(lista_stron1)
	
	lista_stron = []
	if lang.shortName == 'polski':
		for p in lista_stron2:
			if (u'({{język polski}})' in p.text) or (u'({{termin obcy w języku polskim}})' in p.text):
				lista_stron.append(p)
	else:
		for p in lista_stron2:
			s_lang = re.search(re_lang, p.text)
			if s_lang:
			#if u'({{%s}})' % (short) in p.text:
				lista_stron.append(p)
	
	liczba_znakow = 0.0
	liczba_slow = 0.0
	liczba_audio = 0.0
	liczba_grafik = 0.0
	count = 0.0
	countRefs = 0.0
	
	sekcja = re.compile(u'==\s*.*?\(\{\{%s(\|.*?\}\}\)|\}\}\))\s*?==((.*?)==|(.*))' % (re.escape(short)), re.DOTALL)
	#sekcja_wyrazobcy = re.compile(u'\s*.*?\({{termin obcy w języku polskim}}\)\s*?==((.*?)==|(.*))', re.DOTALL)
	polski = re.compile(u'{{tłumaczenia}}.*', re.DOTALL)
	
	usun = []
	usun.append(u'{{odmiana}}')
	usun.append(u'{{etymologia}}')
	usun.append(u'{{wymowa}}')
	usun.append(u'{{znaczenia}}')
	usun.append(u'{{przykłady}}')
	usun.append(u'{{składnia}}')
	usun.append(u'{{kolokacje}}')
	usun.append(u'{{pokrewne}}')
	usun.append(u'{{frazeologia}}')
	usun.append(u'{{uwagi}}')
	usun.append(u'{{synonimy}}')
	usun.append(u'{{antonimy}}')
	usun.append(u'{{źródła}}')
	usun.append(u'{{czytania}}')
	usun.append(u'{{determinatywy}}')
	usun.append(u'{{hanja}}')
	usun.append(u'{{hanja-kreski}}')
	usun.append(u'{{klucz}}')
	usun.append(u'{{kreski}}')
	usun.append(u'{{pochodne}}')
	usun.append(u'{{pole}}')
	usun.append(u'{{trans}}')
	usun.append(u'{{transkr}}')
	usun.append(u'{{transliteracja}}')
	usun.append(u'{{transkrypcja}}')
	usun.append(u'{{warianty}}')
	usun.append(u'{{zapis hieroglificzny}}')
	usun.append(u'{{zch-etymologia}}')
	usun.append(u'{{zch-klucz}}')
	usun.append(u'{{zch-kody}}')
	usun.append(u'{{zch-kolejność}}')
	usun.append(u'{{zch-kreski}}')
	usun.append(u'{{zch-uwagi}}')
	usun.append(u'{{zch-warianty}}')
	usun.append(u'{{zch-znaczenia}}')
	usun.append(u'{{znak-zch}}')
	usun.append(u'{{złożenia}}')
	usun.append(u'<references/>')
	usun.append(u'==')
	usun.append(u'{{IPA([0-9]|)\|}}')
	usun.append(u'\[\[[a-z]*\:.*?\]\]')
	usun.append(u'\'\'przykład\'\'')
	usun.append(u'krótka definicja')
	usun.append(u'\'\'przykład\'\'.*?→ tłumaczenie')
	usun.append(u'\* angielski\: \[\[ \]\]')
	usun.append(u'\n')
	usun.append(u'{{importCStematyczny}}')
	usun.append(u'{{importEO}}')
	usun.append(u'{{ImportEO19}}')
	usun.append(u'{{importFR}}')
	usun.append(u'{{importEL}}')
	usun.append(u'{{importES}}')
	usun.append(u'{{jidyszbot}}')
	usun.append(u'{{importRU}}')
	usun.append(u'{{importSV}}')
	usun.append(u'{{importUK}}')
	usun.append(u'{{importKA}}')
	usun.append(u'{{importAZ}}')
	usun.append(u'{{importIDO}}')
	usun.append(u'{{importEOV}}')
	usun.append(u'{{importIT}}')
	usun.append(u'{{niesprawdzona odmiana}}')
	usun.append(u'({{termin obcy w języku polskim}})')
	usun.append(u'{{Rzeczownik języka polskiego')
	usun.append(u'\|Mianownik lp \=')
	usun.append(u'\|Mianownik lm \=')
	usun.append(u'\|Dopełniacz lp \=')
	usun.append(u'\|Dopełniacz lm \=')
	usun.append(u'\|Celownik lp \=')
	usun.append(u'\|Celownik lm \=')
	usun.append(u'\|Biernik lp \=')
	usun.append(u'\|Biernik lm \=')
	usun.append(u'\|Narzędnik lp \=')
	usun.append(u'\|Narzędnik lm \=')
	usun.append(u'\|Miejscownik lp \=')
	usun.append(u'\|Miejscownik lm \=')
	usun.append(u'\|Wołacz lp \=')
	usun.append(u'\|Wołacz lm \=')
	usun.append(u'{{podobne\|')
	
	wymowa = re.compile(u'{{audio.*?}}')
	grafika = []
	grafika.append(u'\[\[\s*(G|g)rafika\s*\:.*?\]\]')
	grafika.append(u'\[\[\s*(I|i)mage\s*\:.*?\]\]')
	grafika.append(u'\[\[\s*(M|m)edia\s*\:.*?\]\]')
	grafika.append(u'\[\[\s*(F|f)ile\s*\:.*?\]\]')
	grafika.append(u'\[\[\s*(P|p)lik\s*\:.*?\]\]')
	

	usun_join ='|'.join(map(re.escape, usun))
	grafika_join = '|'.join(map(re.escape,grafika))
	for page in lista_stron:
		
		#counting meanings
		count += meanings(page.title, page.text, lang.shortName)
		countRefs += refs(page.title, page.text, lang.shortName)
		
		text = page.text
		'''
		wyraz_obcy = re.search(u'{{termin obcy w języku polskim}}', text)
		if wyraz_obcy:
			text_sekcja = re.search(sekcja_wyrazobcy, text)
		else:
			text_sekcja = re.search(sekcja , text)'''
		text_sekcja = re.search(sekcja , text)
		if text_sekcja:
			newtext0 = re.sub(u':(\s*|)\(1\.1\)(\s*|)\n', u'', text_sekcja.group(2))
			newtext0 = re.sub(u'{{niesprawdzona odmiana.*?\n', u'', newtext0)
			newtext = re.sub(usun_join, '', newtext0)
			newtext1 = " ".join(newtext.split(" "))
			
			newtext2 = re.sub(polski, '', newtext1)
			audio = re.search(wymowa, newtext2)
			if audio:
				liczba_audio += 1.0
			graf = re.search(u'(\[\[(\s*|)((P|p)lik|(F|f)ile|(M|m)edia|(I|i)mage|(G|g)rafika)(\s*|):.*?\]\]|{{litera)', newtext2)
			
			if graf:
				liczba_grafik += 1.0
				newtext3 = re.sub(u'(\[\[(\s*|)((P|p)lik|(F|f)ile|(M|m)edia|(I|i)mage|(G|g)rafika)(\s*|):.[^\|]*|(thumb\||[0-9]*px\||right\||left\||)|{{litera)', '', newtext2)
			else:
				newtext3 = newtext2
			newtext3 = re.sub(u'{{[iI]mportIA\|[^}]*}}', u'', newtext3)
			newtext3 = re.sub(u'{{jidysz\|[^}]*}}', u'', newtext3)
			newtext3 = re.sub(u'{{greka\|[^}]*}}', u'', newtext3)		
			newtext4 = re.sub(u'\[\[[^]]*?\|', u'[[', newtext3)
			liczba_znakow += len(newtext4)
			liczba_slow += 1.0
		else:
			print u'%s - nie znalazł sekcji' % (page.title)
	
	tempShortName = re.sub(u' ', u'_', lang.shortName)
	
	if liczba_slow:	
		dodaj = u'%s\t%.1f\t%.0f\t%.0f\t%.0f\t%.1f\t%.0f\t%.1f\t%.0f\t%.2f\t%.0f\t%.1f\t+\t+\t+\t+\t+\t+\t+\t+\t+\t+\t+\n' % (tempShortName, liczba_znakow/liczba_slow, liczba_slow, liczba_znakow/1000.0, liczba_audio, liczba_audio/liczba_slow*100.0, liczba_grafik, liczba_grafik/liczba_slow*100, count, count/liczba_slow, countRefs, countRefs/liczba_slow*100)
	else:
		dodaj = u''
	file = open(filename, 'a')
	file.write(dodaj.encode( "utf-8" ))
	file.close
	
def meanings(title, text, langShort):
	#counting different meanings in each page
	
	re_count = re.compile('(\: \([0-9]\.[0-9]\))')
	counter = 0.0
	
	word = Haslo(title, text)
	if word.type == 3:
		for lang in word.listLangs:
			if lang.type != 2 and lang.type != 4 and lang.lang == langShort:
				lang.pola()
				if lang.znaczeniaWhole:
					if lang.type != 7:
						s_count = re.findall(re_count, lang.znaczeniaWhole.tresc)
						counter = len(s_count)*1.0
	return counter

def refs(title, text, langShort):
	#counting references
	
	re_refs = re.compile('(<ref>.*?</ref>)')
	re_az = re.compile('[a-z]')

	word = Haslo(title, text)
	if word.type == 3:
		for lang in word.listLangs:
			if lang.type != 2 and lang.type != 4 and lang.lang == langShort:
				s_refs = re.search(re_refs, lang.content)
				if s_refs:
					return 1
				else:
					lang.pola()
					if lang.type == 1 or lang.type ==5 or lang.type == 6 or lang.type == 7 or lang.type == 8:
						if lang.zrodla:
							temp = lang.zrodla.tresc.replace(u'references', u'')
							s_temp = re.search(re_az, temp)
							if s_temp:
								return 1
							else:
								return 0

	return 0


def stat_wikitable():

	site = wikipedia.getSite()
	page_dlugosc = wikipedia.Page(site, u'Wikipedysta:Alkamid/statystyka/długość')
	page_srednia = wikipedia.Page(site, u'Wikipedysta:Alkamid/statystyka/długość_średnia')
	page_multimedia = wikipedia.Page(site, u'Wikipedysta:Alkamid/statystyka/multimedia')
	page_znaczenia = wikipedia.Page(site, u'Wikipedysta:AlkamidBot/statystyka/znaczenia')
	page_znaczenia_templ = wikipedia.Page(site, u'Wikipedysta:AlkamidBot/statystyka/znaczenia/template')
	page_znaczenia_srednia_templ = wikipedia.Page(site, u'Wikipedysta:AlkamidBot/statystyka/znaczenia_średnia/template')
	page_dlugosc_templ = wikipedia.Page(site, u'Wikipedysta:AlkamidBot/statystyka/długość/template')
	page_srednia_templ = wikipedia.Page(site, u'Wikipedysta:AlkamidBot/statystyka/długość_średnia/template')
	page_GraphCount_templ = wikipedia.Page(site, u'Wikipedysta:AlkamidBot/statystyka/liczba_grafik/template')
	page_GraphPerc_templ = wikipedia.Page(site, u'Wikipedysta:AlkamidBot/statystyka/procent_grafik/template')
	page_AudioCount_templ = wikipedia.Page(site, u'Wikipedysta:AlkamidBot/statystyka/liczba_audio/template')
	page_AudioPerc_templ = wikipedia.Page(site, u'Wikipedysta:AlkamidBot/statystyka/procent_audio/template')


	lista = []
	lista_dlug_old = []
	lista_srednia_old = []
	lista_multi_old = []
	lista_znacz_old = []
	inp = codecs.open(filename, encoding='utf-8')

	for line in inp:
		if not line.isspace():
			lista.append(line.split())
	
	def sortkey(row):
		return float(row[2])
	
	lista.sort(key=sortkey, reverse=True)

	text1 = u'{| border=0 cellspacing=0 cellpadding=0\n|\n{| class="wikitable" style="margin: 0px; text-align:right;"\n! miejsce !! zmiana'
	text2 = u'\n|}\n|\n{| class="wikitable sortable" style="margin: 0 auto; white-space: nowrap"\n! język !! suma długości haseł (w tys.) !! zmiana (w tys.) !! liczba haseł\n'
	text3 = text1
	text4 = u'\n|}\n|\n{| class="wikitable sortable" style="margin: 0 auto; white-space: nowrap"\n! język !! średnia długość hasła !! zmiana średniej !! liczba haseł\n'
	text5 = u'{| border=0 cellspacing=0 cellpadding=0\n|\n{| class="wikitable" style="margin: 0px; text-align:right;"\n! miejsce'
	text6 = u'\n|}\n|\n{| class="wikitable sortable" style="margin: 0 auto; white-space: nowrap"\n! język !! % z grafiką !! zmiana % !! z grafiką !! % z nagraniem !! zmiana % !! z nagraniem !! % ze źródłem !! zmiana % !! ze źródłem !! liczba haseł\n'
	text7 = u'\n|}\n|\n{| class="wikitable sortable" style="margin: 0 auto; white-space: nowrap"\n! język !! znaczeń ogółem !! zmiana !! średnia znaczeń w haśle!! zmiana średniej\n'
	text8 = text5
	text9 = u'{{#switch:{{lc:{{{1|}}}}}'
	text10 = text9
	text11 = text9
	text12 = text9
	text13 = text9
	text14 = text9
	text15 = text9
	text16 = text9
	dlug_old = u''
	srednia_old = u''
	multi_old = u''
	znacz_old = u''
	
	for a in lista:
		a[0] = a[0].replace('_', ' ')
	
	i = 1
	
	inp_dlug_old = codecs.open("output/dlugosc_old_%s.txt" % (data_old), encoding='utf-8')
	for line in inp_dlug_old:
		if not line.isspace():
			lista_dlug_old.append(line.split(' - '))
	
	inp_srednia_old = codecs.open("output/srednia_old_%s.txt" % (data_old), encoding='utf-8')
	for line in inp_srednia_old:
		if not line.isspace():
			lista_srednia_old.append(line.split(' - '))
			
	inp_multi_old = codecs.open("output/multi_old_%s.txt" % (data_old), encoding='utf-8')
	for line in inp_multi_old:
		if not line.isspace():
			lista_multi_old.append(line.split(' - '))
			
	inp_znacz_old = codecs.open("output/znacz_old_%s.txt" % (data_old), encoding='utf-8')
	for line in inp_znacz_old:
		if not line.isspace():
			lista_znacz_old.append(line.split(' - '))
	
	countLength = 0.0
			
	zmiana(lista, lista_dlug_old, dlug_old, 3, 12, 13, countLength)
	
	'''	
	
	for a in lista:
		dlug_old = dlug_old + u'%d - %s - %.0f\n' % (i, a[0], float(a[3]))
		countLength += float(a[3])
		for b in lista_dlug_old:
			if (a[0] == b[1]):
				a[12] = int(b[0]) - i
				if (a[12] > 0):
					a[12] = u'+%d' % a[12]
				if (a[12] == 0):
					a[12] = u''
				a[13] = float(a[3]) - float(b[2])
				if (a[13] >= 1.0):
					a[13] = u'+%.0f' % a[13]
				elif (a[13] <= -1.0):
					a[13] = u'%.0f' % a[13]
				else:
					a[13] = u''
		i += 1
	'''	
	i = 1
	
	for a in lista:
		if i<=50:
			text1 = text1 + u'\n|-\n! %d\n! %s' % (i, a[12])
			text2 = text2 + u'|-\n| [[:Kategoria:%s (indeks)|%s]]\n| align="right"| %.0f\n| align="right"| %s\n| align="right"| %.0f\n' % (a[0], a[0], float(a[3]), a[13],float(a[2]))
			i += 1

		text14 = text14 + u'\n|%s=%.1f' % (a[0], float(a[3]))

		
	def sortkey(row):
		return float(row[2])
	
	lista.sort(key=sortkey, reverse=True)

	i = 1
	
	voidCount = 0
	zmiana(lista, lista_srednia_old, srednia_old, 1, 14, 15, voidCount)
	'''
	for a in lista:
		srednia_old = srednia_old + u'%d - %s - %.1f\n' % (i, a[0], float(a[1]))
		
		for b in lista_srednia_old:
			if (a[0] == b[1]):
				a[10] = int(b[0]) - i
				if (a[10] > 0):
					a[10] = u'+%d' % a[10]
				if (a[10] == 0):
					a[10] = u''
				a[11] = float(a[1]) - float(b[2])
				if (a[11] >= 0.1):
					a[11] = u'+%.1f' % a[11]
				elif (a[11] <= -0.1):
					a[11] = u'%.1f' % a[11]
				else:
					a[11] = u''
		i += 1
	'''	
	i = 1
	
	for a in lista:
		if i<=50:
			text3 = text3 + u'\n|-\n! %d\n! %s' % (i, a[14])
			text4 = text4 + u'|-\n| [[:Kategoria:%s (indeks)|%s]]\n| align="right"| %.1f\n| align="right"| %s\n| align="right"| %.0f\n' % (a[0], a[0], float(a[1]), a[15], float(a[2]))
			i += 1
		
		text15 = text15 + u'\n|%s=%.1f' % (a[0], float(a[1]))
		
	def sortkey(row):
		return float(row[2])
	
	lista.sort(key=sortkey, reverse=True)

	i = 1
	
	countAllGraph = 0.0
	countAllAudio = 0.0
	countAllRefs = 0.0
	for a in lista:
		multi_old = multi_old + u'%s - %.1f - %.1f - %.1f\n' % (a[0], float(a[7]), float(a[5]), float(a[11]))
		countAllGraph += float(a[6])
		countAllAudio += float(a[4])
		countAllRefs += float(a[10])
		
		for b in lista_multi_old:
			if (a[0] == b[0]):
				try: b[3]
				except IndexError:
					pass
				else:
					a[16] = float(a[7]) - float(b[1])
					if (a[16] >= 0.1):
						a[16] = u'+%.1f' % a[16]
					elif (a[16] <= -0.1):
						a[16] = u'%.1f' % a[16]
					else:
						a[14] = u''
					
					a[17] = float(a[5]) - float(b[2])
					if (a[17] >= 0.1):
						a[17] = u'+%.1f' % a[17]
					elif (a[17] <= -0.1):
						a[17] = u'%.1f' % a[17]
					else:
						a[17] = u''
					
					print a[18]
					print a[11]
					print b[3]	
					a[18] = float(a[11]) - float(b[3])
					if (a[18] >= 0.1):
						a[18] = u'+%.1f' % a[18]
					elif (a[18] <= -0.1):
						a[18] = u'%.1f' % a[18]
					else:
						a[18] = u''
		i += 1	

	i = 1
	countWords = 0.0
	for a in lista:
		if i<=50:
			text5 = text5 + u'\n|-\n! %d' % (i)
			text6 = text6 + u'|-\n| [[:Kategoria:%s (indeks)|%s]]\n| align="right"| %.1f\n| align="right"| %s\n| align="right"| %.0f\n| align="right"| %.1f\n| align="right"| %s\n| align="right"| %.0f\n| align="right"| %.1f\n| align="right"| %s\n| align="right"| %.0f\n| align="right"| %.0f\n' % (a[0], a[0], float(a[7]), a[14], float(a[6]), float(a[5]), a[15], float(a[4]), float(a[11]), a[18], float(a[10]), float(a[2]))
			i += 1
		text10 = text10 + u'\n|%s=%.0f' % (a[0], float(a[6]))
		text11 = text11 + u'\n|%s=%.0f' % (a[0], float(a[4]))
		text12 = text12 + u'\n|%s=%.1f' % (a[0], float(a[7]))
		text13 = text13 + u'\n|%s=%.1f' % (a[0], float(a[5]))
        print text6
        countWords += float(a[2])

	
	countAllMean = 0.0
	for a in lista:
		znacz_old = znacz_old + u'%s - %.0f - %.4f\n' % (a[0], float(a[8]), float(a[9]))
		countAllMean += float(a[8])
		
		for b in lista_znacz_old:
			if (a[0] == b[0]):
				a[19] = float(a[8])-float(b[1])
				if a[19] >= 0.1:
					a[19] = u'+%.0f' % a[19]
				elif a[19] <= -0.1:
					a[19] = u'%.0f' % a[19]
				else:
					a[19] = u''
					
				a[20] = float(a[9]) - float(b[2])
				if (a[20] >= 0.0001):
					a[20] = u'+%.4f' % a[20]
				elif (a[20] <= -0.0001):
					a[20] = u'%.4f' % a[20]
				else:
					a[20] = u''
					
	i = 1

	def sortkey(row):
		return float(row[8])
	
	lista.sort(key=sortkey, reverse=True)
	
	for a in lista:
		if i<=50:
			text8 = text8 + u'\n|-\n! %d' % (i)
			text7 = text7 + u'|-\n| [[:Kategoria:%s (indeks)|%s]]\n| align="right"| %.0f\n| align="right"| %s\n| align="right"| %.4f\n| align="right"| %s\n' % (a[0], a[0], float(a[8]), a[19], float(a[9]), a[20])
			i += 1
		text9 = text9 + u'\n|%s=%.0f' % (a[0], float(a[8]))
		text16 = text16 + u'\n|%s=%.4f' % (a[0], float(a[9]))
		
	
	text_dlugosc = text1 + text2 + u'|}\n|}'
	text_srednia = text3 + text4 + u'|}\n|}'
	text_multimedia = text5 + text6 + u'|}\n|}'
	text_znaczenia = text8 + text7 + u'|}\n|}'
	text_znaczenia_template = text9 + u'\n|=%.0f\n|data=%s\n|#default=bd.\n}}' % (countAllMean, data_slownie)
	text_GraphCount_template = text10 + u'\n|=%.0f\n|data=%s\n|#default=bd.\n}}' % (countAllGraph, data_slownie)
	text_AudioCount_template = text11 + u'\n|=%.0f\n|data=%s\n|#default=bd.\n}}' % (countAllAudio, data_slownie)
	text_GraphPerc_template = text12 + u'\n|=%.1f|data=%s\n|#default=bd.\n}}' % (countAllGraph/countWords*100, data_slownie)
	text_AudioPerc_template = text13 + u'\n|=%.1f|data=%s\n|#default=bd.\n}}' % (countAllAudio/countWords*100, data_slownie)
	text_dlugosc_template = text14 + u'\n|=%.0f|data=%s\n|#default=bd.\n}}' % (countLength, data_slownie)
	text_srednia_template = text15 + u'\n|=|data=%s\n|#default=bd.\n}}' % (data_slownie)
	text_znaczenia_srednia_template = text16 + u'\n|=%.4f\n|data=%s\n|#default=bd.\n}}' % (countAllMean/countWords, data_slownie)


	
	filename_dlugosc = "output/wikitable-dlugosc.txt"
	filename_srednia = "output/wikitable-srednia.txt"
	filename_multimedia = "output/wikitable-multimedia.txt"
	filename_znaczenia = "output/wikitable-znaczenia.txt"
	filename_dlugosc_old = "output/dlugosc_old_%s.txt" % (data)
	filename_srednia_old = "output/srednia_old_%s.txt" % (data)
	filename_multi_old = "output/multi_old_%s.txt" % (data)
	filename_znacz_old = "output/znacz_old_%s.txt" % (data)

	file = open(filename_dlugosc, 'w')
	file.write(text_dlugosc.encode( "utf-8" ))
	file.close
	file = open(filename_srednia, 'w')
	file.write(text_srednia.encode("utf-8"))
	file.close
	file = open(filename_multimedia, 'w')
	file.write(text_multimedia.encode("utf-8"))
	file.close
	file = open(filename_znaczenia, 'w')
	file.write(text_znaczenia.encode("utf-8"))
	file.close
	file = open(filename_dlugosc_old, 'w')
	file.write(dlug_old.encode("utf-8"))
	file.close
	file = open(filename_srednia_old, 'w')
	file.write(srednia_old.encode("utf-8"))
	file.close
	file = open(filename_multi_old, 'w')
	file.write(multi_old.encode("utf-8"))
	file.close
	file = open(filename_znacz_old, 'w')
	file.write(znacz_old.encode("utf-8"))
	file.close

	
	if (offline_mode == 0):
		#page_dlugosc.put(text_dlugosc, comment="Aktualizacja statystyk, dane z %s" % data_slownie, botflag=False)
		#page_srednia.put(text_srednia, comment="Aktualizacja statystyk, dane z %s" % data_slownie, botflag=False)
		#page_multimedia.put(text_multimedia, comment="Aktualizacja statystyk, dane z %s" % data_slownie, botflag=False)
		#page_znaczenia.put(text_znaczenia, comment="Aktualizacja statystyk, dane z %s" % data_slownie, botflag=False)
		page_dlugosc.put(text_dlugosc, comment="Aktualizacja statystyk, dane z %s" % data_slownie)
		page_srednia.put(text_srednia, comment="Aktualizacja statystyk, dane z %s" % data_slownie)
		page_multimedia.put(text_multimedia, comment="Aktualizacja statystyk, dane z %s" % data_slownie)
		page_znaczenia.put(text_znaczenia, comment="Aktualizacja statystyk, dane z %s" % data_slownie)
		page_znaczenia_templ.put(text_znaczenia_template, comment="Aktualizacja statystyk, dane z %s" % data_slownie)
		page_znaczenia_srednia_templ.put(text_znaczenia_srednia_template, comment="Aktualizacja statystyk, dane z %s" % data_slownie)
		page_dlugosc_templ.put(text_dlugosc_template, comment="Aktualizacja statystyk, dane z %s" % data_slownie)
		page_srednia_templ.put(text_srednia_template, comment="Aktualizacja statystyk, dane z %s" % data_slownie)
		page_GraphCount_templ.put(text_GraphCount_template, comment="Aktualizacja statystyk, dane z %s" % data_slownie)
		page_GraphPerc_templ.put(text_GraphPerc_template, comment="Aktualizacja statystyk, dane z %s" % data_slownie)
		page_AudioCount_templ.put(text_AudioCount_template, comment="Aktualizacja statystyk, dane z %s" % data_slownie)
		page_AudioPerc_templ.put(text_AudioPerc_template, comment="Aktualizacja statystyk, dane z %s" % data_slownie)

def zmiana(lista, listaOld, textOld, whatToCount, changedPlace, changedValue, counter):
		i = 1
		for a in lista:
			textOld = textOld + u'%d - %s - %.0f\n' % (i, a[0], float(a[whatToCount]))
			counter += float(a[whatToCount])
			for b in listaOld:
				if (a[0] == b[1]):
					a[changedPlace] = int(b[0]) - i
					if (a[changedPlace] > 0):
						a[changedPlace] = u'+%d' % a[changedPlace]
					if (a[changedPlace] == 0):
						a[changedPlace] = u''
					a[changedValue] = float(a[whatToCount]) - float(b[2])
					if (a[changedValue] >= 1.0):
						a[changedValue] = u'+%.1f' % a[changedValue]
					elif (a[changedValue] <= -1.0):
						a[changedValue] = u'%.1f' % a[changedValue]
					else:
						a[changedValue] = u''
			i += 1
		
def licznik():
	site = wikipedia.getSite()
	#lista_stron1 = xmlreader.XmlDump('plwiktionary-%s-pages-articles.xml' % data)
	lista_stron1 = xmlreader.XmlDump('/mnt/user-store/dumps/plwiktionary/plwiktionary-%s-pages-articles.xml' % data)
	lista_stron = xmlreader.XmlDump.parse(lista_stron1)
	dlaczego_strona = wikipedia.Page(site, u'Wikisłownik:Dlaczego Wikisłownik')
	presskit = wikipedia.Page(site, u'Wikisłownik:Presskit')
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
	
	if offline_mode:
		print tekst
	else:
		dlaczego_strona.put(tekst, comment = u'Aktualizacja z ostatniego zrzutu bazy danych (%s)' % data_slownie, botflag=False)
		#dlaczego_strona.put(tekst, comment = u'Aktualizacja z ostatniego zrzutu bazy danych (%s)' % data_slownie)
	
	re_presskit_przed = re.compile(u'(.*\* najwięcej słów jest w języku polskim; następne pod względem liczby są: język angielski i sztuczny język interlingua)', re.DOTALL) 
	re_presskit_po = re.compile(u'(== Błędne opinie o Wikisłowniku ==.*)', re.DOTALL)
	
	s_presskit_przed = re.search(re_presskit_przed, presskit.get())
	s_presskit_po = re.search(re_presskit_po, presskit.get())
		
	presskit_tekst = u''
	if s_presskit_przed and s_presskit_po:
		presskit_tekst = s_presskit_przed.group(1)
		presskit_tekst = presskit_tekst + u'\n* ponad %d nagrań wymowy\n* ponad %d ilustracji\n\n' % (liczba_audio, liczba_grafik)
		presskit_tekst = presskit_tekst + s_presskit_po.group(1)
	else:
		print u'coś poszło nie tak\n'
		
	if offline_mode:
		print presskit_tekst
	else:
		presskit.put(presskit_tekst, comment = u'Aktualizacja z ostatniego zrzutu bazy danych (%s)' % data_slownie, botflag=False)
		#presskit.put(presskit_tekst, comment = u'Aktualizacja z ostatniego zrzutu bazy danych (%s)' % data_slownie)

def data_stat():
	
	site = wikipedia.getSite()
	stat = wikipedia.Page(site, u'Wikisłownik:Statystyka')
	
	re_przed = re.compile(u'(.*Zestawienie obejmuje 50 największych \(posiadających najwięcej haseł\) języków na Wikisłowniku. Zanalizowano stan na dzień )', re.DOTALL)
	re_po = re.compile(u'.*Zestawienie obejmuje 50 największych \(posiadających najwięcej haseł\) języków na Wikisłowniku. Zanalizowano stan na dzień.*?(.\n.*)', re.DOTALL)
	
	s_przed = re.search(re_przed, stat.get())
	s_po = re.search(re_po, stat.get())
	
	final = s_przed.group(1) + data_slownie + u', a zmiany podano w stosunku do ' + data_old_slownie + s_po.group(1)
	
	if offline_mode:
		print final
	else:
		stat.put(final, comment=u'zmiana daty')


def main():
	global offline_mode
	offline_mode = 0
	global filename
	filename = "output/statystyka.txt"
	global data
	data = '20110617'
	global data_old
	data_old = '20110603'
	global data_slownie
	data_slownie = data[6] + data[7] + u'.' + data[4] + data[5] + u'.' + data[0] + data[1] + data[2] + data[3]
	global data_old_slownie
	data_old_slownie = data_old[6] + data_old[7] + u'.' + data_old[4] + data_old[5] + u'.' + data_old[0] + data_old[1] + data_old[2] + data_old[3]
	file = open(filename, 'w')
	file.close
	
	for lang in getAllLanguages():
		licz_jezyk(lang)
	
	stat_wikitable()
	licznik()
	data_stat()
	
	
if __name__ == '__main__':
    try:
        main()
    finally:
        wikipedia.stopme()
