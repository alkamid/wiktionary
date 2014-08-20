#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators
import re
from pywikibot import xmlreader
import collections
from klasa import *

		
def czescimowy(data):
	
	data_slownie = data[6] + data[7] + u'.' + data[4] + data[5] + u'.' + data[0] + data[1] + data[2] + data[3]
	site = pywikibot.getSite()
	allowedPage = pywikibot.Page(site, u'Wikipedysta:AlkamidBot/części_mowy/dozwolone')
	outputPage = pywikibot.Page(site, u'Wikipedysta:AlkamidBot/części_mowy/wszystkie')
	allowedPageText = allowedPage.get()
	tempListAllowed = allowedPageText.split(u'\n')
	allowedParts = {}
	cnt = 1
	for elem in tempListAllowed:
		if elem == u'|-':
			mykey = None
			cnt = 1
		if cnt == 1:
			cnt += 1
		elif cnt == 2:
			mykey = elem[1:]
			allowedParts[mykey] = []
			cnt += 1
		elif cnt == 3:
			if elem[1:] != u'':
				tmp = elem[1:].split(u', ')
				for a in tmp:
					allowedParts[mykey].append(a)
			cnt = 1
				
	lista = getListFromXML(data)
	

	re_przyslowie = re.compile(ur'\'\'{{przysłowie .*?}}\'\'$')
	re_forma = re.compile(ur'(\'\'|){{forma (czasownika|rzeczownika|przymiotnika|zaimka|liczebnika|rodzajnika|przysłówka)\|[a-z]*?}}(\'\'|)$')
	re_morfem = re.compile(ur'\'\'{{morfem\|[a-z]*?(}}|\|(przyrostek|przedrostek|przyrostkowy|przedrostkowy)}})\'\'$')
	re_ref = re.compile(ur'\s*<ref.*?(</ref>|/>)\s*')
	re_spacje = re.compile(ur'\'\'(.*?)\'\'$')
	re_zwrotnyFr = re.compile(ur'\'\'\'\'\'(s\'|se ).*?\'\'\', czasownik zwrotny\'\'$')
	re_zwrotny = re.compile(ur'\'\'czasownik zwrotny \'\'\'(.*?)\'\'\'$')
	re_nieprzechodni_dk_ndk = re.compile(ur'\'\'czasownik( (nie|)przechodni|)( (nie|)dokonany|)( lub (nie|)dokonany|)\'\' \({{(n|)dk}} (\[\[(.*?)\]\]|\'\'brak\'\')\)$') #potem można usunąć | z "przechodni" i "dokonany" - wymóg, by wszystkie czasowniki posiadały informację o przechodniości i aspekcie
	re_zwrotny_dk_ndk = re.compile(ur'\'\'czasownik zwrotny( (nie|)dokonany|)( lub (nie|)dokonany|) \'\'\'(.*?)(się|sobie)\'\'\'\'\' \({{(n|)dk}} (\[\[(.*?)(się|sobie)\]\]|\'\'brak\'\')\)$')
	re_zwrotny_sie_in_title = re.compile(ur'\'\'czasownik zwrotny( (nie|)dokonany|)( lub (nie|)dokonany|)\'\' \({{(n|)dk}} (\[\[(.*?)(się|sobie)\]\]|\'\'brak\'\')\)$')
	
	final = u''
	final_input = u''
	tabelka = u'{| class="wikitable"\n!nazwa części mowy\n!przykładowe hasła\n!języki, w których występuje'
	lista_na_wiki = collections.defaultdict()
	
	pretext = u'W poniższych hasłach trzeba poprawić nazwę części mowy. Jeśli znajduje się tutaj poprawny opis części mowy, można go dopisać na [[Wikipedysta:AlkamidBot/części_mowy/dozwolone|listę dozwolonych]]. Jeśli jakiś błąd powtarza się zbyt często, można dopisać go na [[Wikipedysta:AlkamidBot/części_mowy/zamiana|listę automatycznej zamiany]] lub zgłosić to [[Dyskusja wikipedysty:Alkamid|Alkamidowi]]. Ostatnia aktualizacja wg zrzutu bazy danych z %s.\n' % (data_slownie)
	
	for a in lista:
		ifex = 0
		try: h = Haslo(a.title, a.text)
		except sectionsNotFound:
			pass
		except WrongHeader:
			pass
		else:
			if h.type == 3:	
				for c in h.listLangs:
					c.pola()
					if c.type not in (2,3,4,5,7,11):
						for d in c.znaczeniaDetail:
							found = 0
							d[0] = re.sub(re_ref, u'', d[0])
							#generowanie tabelki na wiki
							s_spacje = re.search(re_spacje, d[0])
							temp = d[0]
							if s_spacje:
								temp = u'\'\'%s\'\'' % s_spacje.group(1).strip()
							if allowedParts.has_key(temp):
								if len(allowedParts[temp]) == 0 or c.lang in allowedParts[temp]:
									found = 1
							s_przyslowie = re.search(re_przyslowie, temp)
							s_forma = re.search(re_forma, temp)
							s_morfem = re.search(re_morfem, temp)
							s_zwrotnyFr = re.search(re_zwrotnyFr, temp)
							s_zwrotny = re.search(re_zwrotny, temp)
							s_nieprzechodni_dk_ndk = re.search(re_nieprzechodni_dk_ndk, temp)
							s_zwrotny_dk_ndk = re.search(re_zwrotny_dk_ndk, temp)
							if u'się' in a.title:
								s_zwrotny_sie_in_title = re.search(re_zwrotny_sie_in_title, temp)
							else:
								s_zwrotny_sie_in_title = 0
							
							if not found and not s_przyslowie and not s_forma and not s_morfem and not s_zwrotny and not s_zwrotnyFr and not s_zwrotny_dk_ndk and not s_nieprzechodni_dk_ndk and not s_zwrotny_sie_in_title:
								try: lista_na_wiki[temp]
								except KeyError:
									lista_na_wiki[temp] = collections.defaultdict()
									lista_na_wiki[temp]['samples'] = []
									lista_na_wiki[temp]['langs'] = []
									if h.title not in lista_na_wiki[temp]['samples']:
										lista_na_wiki[temp]['samples'].append(h.title)
									if c.lang not in lista_na_wiki[temp]['langs']:
										lista_na_wiki[temp]['langs'].append(c.lang)
								else:
									if h.title not in lista_na_wiki[temp]['samples']:
										lista_na_wiki[temp]['samples'].append(h.title)
									if c.lang not in lista_na_wiki[temp]['langs']:
										lista_na_wiki[temp]['langs'].append(c.lang)
								ifex = 1
				if ifex:
					final_input += u'\n%s' % (h.title)	
										
	for key in sorted(lista_na_wiki.iterkeys()):
		tabelka += u'\n|-\n|%s\n|' % key
		i = 0
		for a in lista_na_wiki[key]['samples']:
			if i<10:
				tabelka += u'[[%s]]' % a
				if i<9:
					tabelka += u', '
				i += 1
		tabelka += u'\n|'
		if len(lista_na_wiki[key]['langs'])<10:
			for b in lista_na_wiki[key]['langs']:
				tabelka += u'%s, ' % b
			
	tabelka += u'\n|}'
	
	outputPage.put(pretext + u'\n' + tabelka, comment=u"Aktualizacja listy", botflag=False)
	
	file = open("output/czescimowy_tabelka.txt", 'w')
	file.write(tabelka.encode("utf-8"))
	file.close
	
	file = open("output/czescimowy_input.txt", 'w')
	file.write(final_input.encode("utf-8"))
	file.close
