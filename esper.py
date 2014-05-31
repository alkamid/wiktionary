#!/usr/bin/python
# -*- coding: utf-8 -*-

# zmiany w esperanto: rozbicie na dwa języki, eo i eom

import codecs
from pywikibot import Category
import pywikibot
from pywikibot import pagegenerators
import re
import math
import datetime
from klasa import *

def main():
	
	site = pywikibot.getSite()
	cat = Category(site,u'Kategoria:esperanto (indeks)')
	lista = pagegenerators.CategorizedPageGenerator(cat, start='anemi')
	#, start=u'abduktoro'
	re_etymn = re.compile(ur'\{\{etymn\|eo\|(.*?)\}\}')
	re_etymn_nr = re.compile(ur'(\:\s*?\([0-9]\.[0-9]\))\s*?\{\{etymn\|eo\|(.*?)\}\}(.*?)\n')
	
	czesciMowy = [u'rzeczownik', u'czasownik', u'przymiotnik', u'przysłówek', u'spójnik', u'liczebnik', u'zaimek', u'wykrzyknik', u'partykuła']
	#lista = [pywikibot.Page(site, u'aboc')]
	for word in lista:
		a = word.title()
		
		h = Haslo(a)
		if h.type == 3:
			morfem = 0
			etymn = 0
			pochodne = 0
			pokrewne = 0
			inneCzesci = 0
			skrot = 0
			for b in h.listLangs:
				b.pola()
				morfologia = u''
				if (b.type == 1 or b.type == 10) and b.lang == u'esperanto' and b.znaczeniaDetail:
					b.etymologia.numer()
					for c in b.znaczeniaDetail:
						if c[0] == u'{{morfem|eo}}' or c[0] == u'{{morfem|eo|przedrostkowy}}':
							morfem = 1
						if any(e in c[0] for e in czesciMowy):
							inneCzesci = 1
						if u'skrót' in c[0]:
							skrot = 1
					wordCount = len(b.title.split())
					if u'{{pochodne}}' in b.content:
						pochodne = 1
					if u'{{etymn' in b.etymologia.text:
						etymn = 1
					try: b.pokrewne
					except AttributeError:
						pass
					else:
						pokrewne = 1
					#print u'type = %d, morfem = %d, inneCzesci = %d, skrot = %d, pochodne = %d, etymn = %d, pokrewne = %d' % (b.type, morfem, inneCzesci, skrot, pochodne, etymn, pokrewne)
					
					if b.type == 1 and not morfem and not pochodne and pokrewne and (etymn or wordCount>1 or skrot):
						if b.etymologia.type == 2:
							for elem in b.etymologia.list:
								s_etymn = re.findall(re_etymn, elem[1])
								elem[1] = re.sub(re_etymn, u'', elem[1])
								if s_etymn:
									morfologia += u'\n' + elem[0]
									for c in s_etymn:
										morfologia += u' {{morfeo|%s}}' % (c)
								if elem[1].strip() == u'':
									elem[0] = u''
									elem[1] = u''
								else:
									elem[1] = elem[1].strip(u' ')
									elem[1] = u' ' + elem[1]
							b.dodatki.text += u'\n{{morfologia}}' + morfologia
							b.saveChanges()
						elif b.etymologia.type == 1:
							s_etymn = re.findall(re_etymn, b.etymologia.text)
							b.etymologia.text = re.sub(re_etymn, u'', b.etymologia.text)
							b.etymologia.text = b.etymologia.text.strip(u' ')
							if b.etymologia.text != u'':
								b.etymologia.text = u' ' + b.etymologia.text
							for elem in s_etymn:
								morfologia += u' {{morfeo|%s}}' % elem
							b.dodatki.text += u'\n{{morfologia}}' + morfologia
							b.saveChanges()
					elif b.type == 10 and morfem and pochodne and not etymn and not pokrewne and not inneCzesci:
						b.naglowek.text = b.naglowek.text.replace(u'{{esperanto}}', u'{{esperanto (morfem)}}')
						b.saveChanges()
					else:
						b.uwagi.text += u' {{zmiany-w-esperanto}}'
						b.saveChanges()
			
			history = word.getVersionHistory()
			done = 0
			for elem in history:
				if elem[3] == u'reorganizacja esperanto (wydzielenie morfemów do osobnego języka)' and elem[2] == u'AlkamidBot':
					done = 1

			if not done:
				h.push(False, u'reorganizacja esperanto (wydzielenie morfemów do osobnego języka)')
	
	

if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
