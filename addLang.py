#!/usr/bin/python
# -*- coding: utf-8 -*-

'''This script adds necessary pages/templates for a new language - what takes a human a few minutes, it does automatically'''

import pywikibot
from pywikibot import pagegenerators
import re
import collections
from klasa import *
import datetime
import time
	
def main():
	site = pywikibot.getSite()
	
	'''Start input - remember to change the variables below!'''
	
	shortName = u'czukocki' #short language name, i.e. without "język"
	shortOnly = 0 #some languages are referred to by their name only, e.g. "esperanto" (not "esperanto language") - in that case, set shortOnly to 1
	kod = u'ckt' #wikimedia or ISO code
	jakie = u'czukockie' #adjective: polski -> polskie, esperanto -> esperanckie, volapuk -> volapuk
	zjezyka = u'czukockiego' #"z języka polskiego", "z esperanto", "z języka akan"
	etymSkr = u'czuk' #abbreviation to use in {{etym}} template, chosen arbitrarily
	
	'''End input'''
	
	
	if shortOnly:
		longName = shortName
	else:
		longName = u'język %s' % shortName
		
	#some templates/pages use "Język xxx", others use "język xxx"
	longNameCapital = longName[0].upper() + longName[1:]
	
	#kolejne czynności z http://pl.wiktionary.org/wiki/Wikis%C5%82ownik:Struktura_j%C4%99zyka_w_Wikis%C5%82owniku
	
	#1. kategoria główna
	page1 = pywikibot.Page(site, u'Kategoria:%s' % longNameCapital)
	try: page1.get()
	except pywikibot.NoPage:
		textPage1 = u'{{kategoria języka\n|nazwa polska=%s\n|nazwa własna=\n|język krótko=%s\n|z języka=%s\n|przysłowia=\n|podręcznik=\n|tworzenie haseł=\n|nagrania wymowy=\n|dodatkowe=\n}}\n\n[[Kategoria:Języki|%s]]' % (longNameCapital, shortName, zjezyka, shortName)
		page1.put(textPage1, comment=u"Dodanie języka %s" % zjezyka)
		#print textPage1
	else:
		pywikibot.output(u'Kategoria języka "%s" już istnieje!' % shortName)
	
	#2. kategoria indeks
	page2 = pywikibot.Page(site, u'Kategoria:%s (indeks)' % shortName)
	try: page2.get()
	except pywikibot.NoPage:
		textPage2 = u'<div align=center>\'\'\'[[:Kategoria:%s|%s]]\'\'\'<p>{{indeks|%s}}</div>\n{{dodajhasło}}\n[[Kategoria:Indeks słów wg języków]]\n[[Kategoria:%s| ]]' % (longNameCapital, longNameCapital, shortName, longNameCapital)
		page2.put(textPage2, comment=u"Dodanie języka %s" % zjezyka)
		#print textPage2
	else:
		pywikibot.output(u'Kategoria z indeksem języka "%s" już istnieje!' % shortName)
	
	#3. szablon języka
	page3 = pywikibot.Page(site, u'Szablon:%s' % longName)
	try: page3.get()
	except pywikibot.NoPage:
		textPage3 = u'<includeonly>{{nagłówek języka\n| długa          = %s\n| krótka         = %s\n| kod            = %s\n| klucz_indeksu	= {{{1|{{PAGENAME}}}}}\n}}</includeonly><noinclude>[[Kategoria:Szablony indeksujące języków| {{PAGENAME}}]]</noinclude>' % (longName, shortName, kod)
		page3.put(textPage3, comment=u"Dodanie języka %s" % zjezyka)
		#print textPage3
	else:
		pywikibot.output(u'Szablon języka "%s" już istnieje!' % shortName)
		
	#4. {{licznik}}
	page4 = pywikibot.Page(site, u'Szablon:licznik')
	if u':%s ' % shortName not in page4.get():
		zaczepienie = u'0\n}}}}<noinclude>'
		re_before = re.compile(ur'(.*?)%s' % re.escape(zaczepienie), re.DOTALL)
		re_after = re.compile(ur'.*?(%s.*)' % re.escape(zaczepienie), re.DOTALL)
		s_before = re.search(re_before, page4.get())
		s_after = re.search(re_after, page4.get())
		if s_before and s_after:
			textPage4 = s_before.group(1)
			textPage4 += u'{{PAGESINCAT:%s (indeks)|R}}+\n' % shortName
			textPage4 += s_after.group(1)
			page4.put(textPage4, comment=u"Dodanie języka %s" % zjezyka)
			#print textPage4
		else:
			pywikibot.output(u'Nie dodano parametru do szablonu {{licznik}}!')
	else:
		pywikibot.output(u'Nazwa języka (%s) istnieje już  w szablonie {{licznik}}' % shortName)
		
	#5. {{indeks}}
	page5 = pywikibot.Page(site, u'Szablon:indeks')
	if u'|%s=' % shortName not in page5.get():
		zaczepienie = u' |#default=\'Brak parametru. [http://pl.wiktionary.org/w/index.php?title=Wikis%C5%82ownik:Zg%C5%82o%C5%9B_b%C5%82%C4%85d_w_ha%C5%9Ble&action=edit&section=new Zgłoś problem].\''
		re_before = re.compile(ur'(.*?)%s' % re.escape(zaczepienie), re.DOTALL)
		re_after = re.compile(ur'.*?(%s.*)' % re.escape(zaczepienie), re.DOTALL)
		s_before = re.search(re_before, page5.get())
		s_after = re.search(re_after, page5.get())
		if s_before and s_after:
			textPage5 = s_before.group(1)
			textPage5 += u' |%s={{indeks/nowy|%s}}\n' % (shortName, shortName)
			textPage5 += s_after.group(1)
			page5.put(textPage5, comment=u"Dodanie języka %s" % zjezyka)
			#print textPage5
		else:
			pywikibot.output(u'Nie dodano parametru do szablonu {{indeks}}!')
	else:
		pywikibot.output(u'Nazwa języka (%s) istnieje już  w szablonie {{indeks}}' % shortName)
		
	#6. {{dopracować}}
	page6 = pywikibot.Page(site, u'Szablon:dopracować')
	if u' %s=' % shortName not in page6.get():
		zaczepienie = u' |#default=Należy w nim poprawić: \'\'{{{1}}}\'\'[[Kategoria:Hasła do dopracowania|{{BASEPAGENAME}}]]'
		re_before = re.compile(ur'(.*?)%s' % re.escape(zaczepienie), re.DOTALL)
		re_after = re.compile(ur'.*?(%s.*)' % re.escape(zaczepienie), re.DOTALL)
		s_before = re.search(re_before, page6.get())
		s_after = re.search(re_after, page6.get())
		if s_before and s_after:
			textPage6 = s_before.group(1)
			textPage6 += u' | %s=[[Kategoria:Hasła %s do dopracowania|{{BASEPAGENAME}}]]\n' % (shortName, jakie)
			textPage6 += s_after.group(1)
			page6.put(textPage6, comment=u"Dodanie języka %s" % zjezyka)
			#print textPage6
		else:
			pywikibot.output(u'Nie dodano parametru do szablonu {{dopracować}}!')
	else:
		pywikibot.output(u'Nazwa języka (%s) istnieje już w szablonie {{dopracować}}' % shortName)
	
	#7. skróty do sekcji
	page7 = pywikibot.Page(site, u'Wikisłownik:Kody języków')
	if u' %s\n' % shortName not in page7.get():
		zaczepienie = u'|}\n\n== Linki zewnętrzne'
		re_before = re.compile(ur'(.*?)%s' % re.escape(zaczepienie), re.DOTALL)
		re_after = re.compile(ur'.*?(%s.*)' % re.escape(zaczepienie), re.DOTALL)
		s_before = re.search(re_before, page7.get())
		s_after = re.search(re_after, page7.get())
		if s_before and s_after:
			textPage7 = s_before.group(1)
			textPage7 += u'|-\n|%s\n|%s\n' % (longName, kod)
			textPage7 += s_after.group(1)
			page7.put(textPage7, comment=u"Dodanie języka %s" % zjezyka)
			#print textPage7
		else:
			pywikibot.output(u'\n----------------------------------------\nNie dodano parametru do strony Wikisłownik:Kody języków!\n--------------------\n')
	else:
		pywikibot.output(u'Nazwa języka (%s) istnieje już na stronie Wikisłownik:Kody języków' % shortName)
	
	#7a. etymologia - kategoria
	page71 = pywikibot.Page(site, u'Kategoria:%s w etymologii' % longNameCapital)
	try: page1.get()
	except pywikibot.NoPage:
		textPage71 = u'__HIDDENCAT__\n[[Kategoria:%s| ]]\n[[Kategoria:Relacje etymologiczne|%s]]' % (longNameCapital, shortName)
		page71.put(textPage71, comment=u"Dodanie języka %s" % zjezyka)
		#print textPage1
	else:
		pywikibot.output(u'Kategoria etymologiczna języka "%s" już istnieje!' % shortName)
		
	#7b. etymologia Szablon:etym/język
	
	page72 = pywikibot.Page(site, u'Szablon:etym/język')
	if u'%s\n' % shortName not in page72.get():
		if u' %s=' % (etymSkr) not in page72.get():
			zaczepienie = u' |inny\n}}<noinclude>'
			re_before = re.compile(ur'(.*?)%s' % re.escape(zaczepienie), re.DOTALL)
			re_after = re.compile(ur'.*?(%s.*)' % re.escape(zaczepienie), re.DOTALL)
			s_before = re.search(re_before, page72.get())
			s_after = re.search(re_after, page72.get())
			if s_before and s_after:
				textPage72 = s_before.group(1)
				textPage72 += u' |%s=%s\n' % (etymSkr, longNameCapital)
				textPage72 += s_after.group(1)
				page72.put(textPage72, comment=u"Dodanie języka %s" % zjezyka)
				#print textPage7
			else:
				pywikibot.output(u'Nie dodano parametru do szablonu {{etym/język}}!')
		else:
			pywikibot.output(u'Taki skrót już istnieje w {{etym/język}}, wybierz inny')
	else:
		pywikibot.output(u'Nazwa języka (%s) istnieje już w szablonie {{etym/język}}' % shortName)
	


	#9. MediaWiki:Gadget-false-blue-links.js
	page9 = pywikibot.Page(site, u'MediaWiki:Gadget-false-blue-links.js')
	if u'"%s"' % (shortName) not in page9.get():
		zaczepienie = u'\n  };\n  /*var tab="";\n  for (var jezyk in om$Lang2Code)'
		re_before = re.compile(ur'(.*?)%s' % re.escape(zaczepienie), re.DOTALL)
		re_after = re.compile(ur'.*?(%s.*)' % re.escape(zaczepienie), re.DOTALL)
		s_before = re.search(re_before, page9.get())
		s_after = re.search(re_after, page9.get())
		if s_before and s_after:
			textPage9 = s_before.group(1)
			textPage9 += u',\n	"%s"	:"%s"' % (shortName, kod)
			textPage9 += s_after.group(1)	
			page9.put(textPage9, comment=u"Dodanie języka %s" % zjezyka, as_group='sysop')
			#print textPage9
		else:
			pywikibot.output(u'Nie dodano parametru do strony MediaWiki:Gadget-false-blue-links.js!')
	else:
		pywikibot.output(u'Nazwa języka (%s) istnieje już na stronie MediaWiki:Gadget-false-blue-links.js' % shortName)

	#9. MediaWiki:Common.js
	page10 = pywikibot.Page(site, u'MediaWiki:Common.js')
	if u'"%s"' % (shortName) not in page10.get():
		zaczepienie = u'\n	};\n}\n\nvar om$sectionLinksProcessed=false;\nfunction om$sectionLinks()'
		re_before = re.compile(ur'(.*?)%s' % re.escape(zaczepienie), re.DOTALL)
		re_after = re.compile(ur'.*?(%s.*)' % re.escape(zaczepienie), re.DOTALL)
		s_before = re.search(re_before, page10.get())
		s_after = re.search(re_after, page10.get())
		if s_before and s_after:
			textPage10 = s_before.group(1)
			textPage10 += u',\n	"%s"	:"%s"' % (shortName, kod)
			textPage10 += s_after.group(1)
			page10.put(textPage10, comment=u"Dodanie języka %s" % zjezyka, as_group='sysop')
			#print textPage10
		else:
			pywikibot.output(u'Nie dodano parametru do strony MediaWiki:Common.js!')
	else:
		pywikibot.output(u'Nazwa języka (%s) istnieje już na stronie MediaWiki:Common.js' % shortName)

	#8. joystick/liczone
	page8 = pywikibot.Page(site, u'Wikipedysta:Joystick/statystyka/liczone')
	
	# new version (without the first column consisting of numbers)
	if u' %s ' % shortName not in page8.get():
		zaczepienie = u'}}\n<tr class="sortbottom">\n<td/>\n<td align=right>\'\'\'Razem:\'\'\'</td>\n<td align=right><small>100%</small></td>'
		re_before = re.compile(ur'(.*?)%s' % re.escape(zaczepienie), re.DOTALL)
		re_after = re.compile(ur'.*?(%s.*)' % re.escape(zaczepienie), re.DOTALL)
		s_before = re.search(re_before, page8.get())
		s_after = re.search(re_after, page8.get())
		if s_before and s_after:
			textPage8 = s_before.group(1)
			if shortOnly:
				textPage8 += u'|{{Wikisłownik:STAT/ramka| %s | w=x | }}\n' % shortName
			else:
				textPage8 += u'|{{Wikisłownik:STAT/ramka| %s | }}\n' % shortName
			textPage8 += s_after.group(1)
			page8.put(textPage8, comment=u"Dodanie języka %s" % zjezyka, as_group='sysop')
		else:
			pywikibot.output(u'Nie dodano parametru do strony Wikipedysta:Joystick/statystyka/liczone! (najprawdopodobniej strona została przez kogoś zmieniona)')
	else:
		pywikibot.output(u'Nazwa języka (%s) istnieje już na stronie Wikipedysta:Joystick/statystyka/liczone' % shortName)
			
	# old version (with numbered rows)		
	'''if u' %s ' % shortName not in page8.get():
		zaczepienie = u'|- class="sortbottom"\n| align=right | \'\'\'Razem:\'\'\'\n| align=right | <small>100%</small> '

		re_before1 = re.compile(ur'(.*?! [0-9]{3}\n)\|- class="sortbottom" \n\| &nbsp;', re.DOTALL)
		re_after1 = re.compile(ur'.*?! [0-9]{3}\n(\|- class="sortbottom" \n\| &nbsp;.*)', re.DOTALL)
		re_int = re.compile(ur'.*?! ([0-9]{3})\n\|- class="sortbottom" \n\| &nbsp;', re.DOTALL)
		s_int = re.search(re_int, page8.get())
		s_before1 = re.search(re_before1, page8.get())
		s_after1 = re.search(re_after1, page8.get())
		if s_before1 and s_after1:	
			nextInt = int(s_int.group(1)) + 1
			re_before = re.compile(ur'(.*?)%s' % re.escape(zaczepienie), re.DOTALL)
			re_after = re.compile(ur'.*?(%s.*)' % re.escape(zaczepienie), re.DOTALL)
			s_after1.group(1)
			s_before = re.search(re_before, s_after1.group(1))
			s_after = re.search(re_after, s_after1.group(1))
			if s_before and s_after:
				textPage8 = s_before1.group(1)
				textPage8 += u'|-\n! %d\n' % nextInt
				textPage8 += s_before.group(1)
				if shortOnly:
					textPage8 += u'{{User:Joystick/statystyka/ramka| %s | w=x | }}\n' % shortName
				else:
					textPage8 += u'{{User:Joystick/statystyka/ramka| %s | }}\n' % shortName
				textPage8 += s_after.group(1)
				page8.put(textPage8, comment=u"Dodanie języka %s" % zjezyka)
				#print textPage8
			else:
				print u'Nie dodano parametru do strony Wikipedysta:Joystick/statystyka/liczone! (najprawdopodobniej strona została przez kogoś zmieniona)'
		else:
			print u'Nie dodano parametru do strony Wikipedysta:Joystick/statystyka/liczone! (najprawdopodobniej strona została przez kogoś zmieniona)'
	else:
		print u'Nazwa języka (%s) istnieje już na stronie Wikipedysta:Joystick/statystyka/liczone' % shortName'''
	
if __name__ == '__main__':
	try:
		main()
	finally:
		pywikibot.stopme()

