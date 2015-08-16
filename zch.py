#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
#sys.path.append('/home/adam/pywiki/pywikipedia')
sys.path.append('/home/alkamid/wikt/pywikipedia')
import pywikibot
from pywikibot import Category
from pywikibot import pagegenerators
import re

def main():
	test_mode = 0;
	site = pywikibot.getSite()
	site_en = pywikibot.getSite('en', 'wiktionary')
	site_com = pywikibot.getSite('commons', 'commons')
	cat = Category(site,'Kategoria:japoński (indeks)')
	lista_stron = pagegenerators.CategorizedPageGenerator(cat)
	log_site = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/zch/log')
	
	lista = []
	istnieje = []
	
	han_char = re.compile('{{Han(_| )char\|(.*?)}')
	han_ref = re.compile('{{Han(_| )ref\|(.*})')
	zh_f = re.compile('{{zh-forms\|(.*)}')
	jap_f = re.compile('{{ja-forms\|(.*)}')
	kx = re.compile('kx=(.*?)(\||})')
	dkj = re.compile('\|dkj=(.*?)(\||})')
	dj = re.compile('\|dj=(.*?)(\||})')
	hdz = re.compile('\|hdz=(.*?)(\||})')
	rn = re.compile('rn=([0-9]*?)\|')
	rad = re.compile('rad=(.)')
	han_as = re.compile('as=([0-9]*?)\|')
	sn = re.compile('sn=([0-9]*?)\|')
	canj = re.compile('canj=([^\|]*)')
	cr = re.compile('four=(.*?)\|')
	alt = re.compile('alt=(.*?)\|')
	asj = re.compile('asj=(.*?)\|')
	tekst_przed = re.compile('(.*?)=', re.DOTALL)
	tekst_po = re.compile('.*?(=.*)', re.DOTALL)
	grafika = re.compile('(\-bw\.|\-red\.|\-order\.|{{zch\-cienie}}|{{zch\-animacja}}|{{zch\-komiks}})')
	
	for page in lista_stron:
		if len(page.title())==1:
			lista.append(page)
	
		
	for a in lista:
		tekst = ''
		
		rn_abort = 0
		rad_abort = 0
		han_as_abort = 0
		sn_abort = 0
		canj_abort = 0
		cr_abort = 0
		
		try:
			strona = a.get()
		except pywikibot.IsRedirectPage:
			print('[[%s]] - przekierowanie' % a.title())
			log = log + '\n*[[%s]] - przekierowanie' % a.title()
		except pywikibot.Error:
			print('[[%s]] - błąd' % a.title())
			log = log + '\n*[[%s]] - błąd' % a.title()
		else:
			
			tekst_przed_s = re.search(tekst_przed, a.get())
			tekst_po_s = re.search(tekst_po, a.get())
			
			log = ''
			
			if test_mode == 1:
				sekcja_znak = 'fdssagrefadf'
			else:
				sekcja_znak = '{{znak chiński}}'
			
			if sekcja_znak in a.get():
				print('[[%s]] - istnieje już sekcja {{znak chiński}}' % a.title())
				log = log + '\n*[[%s]] - istnieje już sekcja {{s|znak chiński}}' % a.title()
				istnieje.append(a)
			else:
				ang = pywikibot.Page(site_en, a.title())
				han_char_s = re.search(han_char, ang.get())
			
				grafika_s = re.search(grafika, a.get())
				if grafika_s != None:
					print('[[%s]] - znaleziono grafikę z CJK stroke order' % a.title())
					log = log + '\n*[[%s]] - znaleziono grafikę z CJK stroke order' % a.title()
			
				if han_char_s != None:
				
					szablon_han = han_char_s.group(2)
									 
					rn_s = re.search(rn, szablon_han)
					rad_s = re.search(rad, szablon_han)
					han_as_s = re.search(han_as, szablon_han)
					sn_s = re.search(sn, szablon_han)
					canj_s = re.search(canj, szablon_han)
					cr_s = re.search(cr, szablon_han)
					alt_s = re.search(alt, szablon_han)
					asj_s = re.search(asj, szablon_han)
				
					if alt_s == None:
						alter = 0
					else:
						if alt_s.group(1) == '':
							alter = 0
						else:
							alter = 1
					if asj_s == None:
						alter1 = 0
					else:
						if asj_s.group(1) == '':
							alter1 = 0
						else:
							alter1 = 1
						
					if alter == 0 and alter1 == 0:			
				
						#print a.title()
						if rn_s == None:
							print('[[%s]] - Nie istnieje argument \'rn\'' % a.title())
							log = log + '\n*[[%s]] - Nie istnieje argument \'rn\'' % a.title()
							rn_abort = 1
						if rad_s == None:
							print('[[%s]] - Nie istnieje argument \'rad\'' % a.title())
							log = log + '\n*[[%s]] - Nie istnieje argument \'rad\'' % a.title()
							rad_abort = 1
						if han_as_s != None:
							#print han_as_s.group(1)
							if han_as_s.group(1) == '0' or han_as_s.group(1) =='00':
								as_output = '+ 0'
							else:
								if han_as_s.group(1)[0] == '0':
									as_output = '+ %s' % han_as_s.group(1)[1]
								else:
									as_output = han_as_s.group(1)[1]
							#print as_output
						else:

							han_as_abort = 1
						if sn_s == None:

							sn_abort = 1
						if canj_s == None:

							canj_abort = 1
						if cr_s != None:
							if cr_s.group(1).isspace() or cr_s.group(1) == '':
								print('[[%s]] - argument \'four\' na en.wikt jest pusty - dodać ręcznie' % a.title())
								log = log + '\n*[[%s]] - argument \'four\' na en.wikt jest pusty - dodać ręcznie' % a.title()
						else:
							cr_abort = 1
				
						kolejnosc_koncowa_c = ''
						
						if pywikibot.ImagePage(site_en, '%s-bw.png' % a.title()).fileIsShared():
							kolejnosc_koncowa_c = '{{zch-komiks}}'
						else:
							if pywikibot.ImagePage(site_en, '%s-red.png' % a.title()).fileIsShared():
								kolejnosc_koncowa_c = '{{zch-cienie}}'
							else:
								if pywikibot.ImagePage(site_en, '%s-order.gif' % a.title()).fileIsShared():
									kolejnosc_koncowa_c = '{{zch-animacja}}'

						
						kolejnosc_koncowa_j = ''
						
						if pywikibot.ImagePage(site_en, '%s-jbw.png' % a.title()).fileIsShared():
							kolejnosc_koncowa_j = '{{zch-komiks|j}}'
						else:
							if pywikibot.ImagePage(site_en, '%s-jred.png' % a.title()).fileIsShared():
								kolejnosc_koncowa_j = '{{zch-cienie|j}}'
							else:
								if pywikibot.ImagePage(site_en, '%s-jorder.gif' % a.title()).fileIsShared():
									kolejnosc_koncowa_j = '{{zch-animacja|j}}'

						
						kolejnosc_koncowa_t = ''
						
						if pywikibot.ImagePage(site_en, '%s-tbw.png' % a.title()).fileIsShared():
							kolejnosc_koncowa_t = '{{zch-komiks|t}}'
						else:
							if pywikibot.ImagePage(site_en, '%s-tred.png' % a.title()).fileIsShared():
								kolejnosc_koncowa_t = '{{zch-cienie|t}}'
							else:
								if pywikibot.ImagePage(site_en, '%s-torder.gif' % a.title()).fileIsShared():
									kolejnosc_koncowa_t = '{{zch-animacja|t}}'
								
									
						kolejnosc_koncowa_a = ''
						
						if pywikibot.ImagePage(site_en, '%s-abw.png' % a.title()).fileIsShared():
							kolejnosc_koncowa_a = '{{zch-komiks|a}}'
						else:
							if pywikibot.ImagePage(site_en, '%s-ared.png' % a.title()).fileIsShared():
								kolejnosc_koncowa_a = '{{zch-cienie|a}}'
							else:
								if pywikibot.ImagePage(site_en, '%s-aorder.gif' % a.title()).fileIsShared():
									kolejnosc_koncowa_a = '{{zch-animacja|a}}'
						
																						
						tekst = '== {{zh|%s}} ({{znak chiński}}) ==\n{{klucz}}' % a.title()	
					
						if rn_abort or rad_abort or han_as_abort:
							print('[[%s]] - w en.wikt nie istnieje któryś z argumentów do {{klucz}} - dodać ręcznie' % a.title())
							log = log + '\n*[[%s]] - w en.wikt nie istnieje któryś z argumentów do {{s|klucz}} - dodać ręcznie' % a.title()
						else:
							tekst = tekst + ' %s %s %s' % (rn_s.group(1), rad_s.group(1), as_output)
					
						tekst = tekst + '\n{{kreski}}'
						if sn_abort:
							print('[[%s]] - w en.wikt nie istnieje argument do {{kreski}} - dodać ręcznie')
							log = log + '\n*[[%s]] - w en.wikt nie istnieje argument do {{s|kreski}} - dodać ręcznie'
						else:
							tekst = tekst + ' %s\n' % sn_s.group(1)
						
						zh_f_s = re.search(zh_f, ang.get())	
						ja_f_s = re.search(jap_f, ang.get())
						
						warianty = '{{warianty'
						warianty_obr = '{{warianty-obrazek'
						ku = ''
						xu = ''
						sou = ''
						sot = ''
						ming = ''
						upr = ''
						trad = ''
						shin = ''
						
						
						if zh_f_s != None:
							zh_f_str = zh_f_s.group(1).replace("[","").replace("]","").replace("{{zh-lookup|", "").replace("}", "")
							zh_osobno = zh_f_str.split('|')
							warianty = warianty + ' | {{zch-w|ct|%s}} | {{zch-w|cu|%s}}' % (zh_osobno[1], zh_osobno[0])

							
						if ja_f_s != None:
							ja_f_str = ja_f_s.group(1).replace("[","").replace("]","").replace("{{zh-lookup|", "").replace("}", "")
							ja_osobno = ja_f_str.split('|')
							warianty = warianty + ' | {{zch-w|js|%s}} | {{zch-w|ct|%s}} | {{zch-w|cu|%s}}' % (ja_osobno[0], ja_osobno[2], ja_osobno[1])
							trad = ja_osobno[2]
							upr = ja_osobno[1]
							shin = ja_osobno[0]							
						
						
						if pywikibot.ImagePage(site_en, '%s-clerical.svg' % a.title()).fileIsShared():
							warianty_obr = warianty_obr + ' | {{zch-obrazek|c|%s}}' % a.title()
						else:
							if pywikibot.ImagePage(site_en, '%s-clerical.png' % a.title()).fileIsShared():
								warianty_obr = warianty_obr + ' | {{zch-obrazek|c|%s|p}}' % a.title()
							else:
								if pywikibot.ImagePage(site_en, '%s-clerical.gif' % a.title()).fileIsShared():
									warianty_obr = warianty_obr + ' | {{zch-obrazek|c|%s|g}}' % a.title()
				
					
					
						if pywikibot.ImagePage(site_en, '%s-xinshu.svg' % a.title()).fileIsShared():
							warianty_obr = warianty_obr + ' | {{zch-obrazek|xt|%s}}' % a.title()
						else:
							if pywikibot.ImagePage(site_en, '%s-xinshu.png' % a.title()).fileIsShared():
								warianty_obr = warianty_obr + ' | {{zch-obrazek|xt|%s|p}}' % a.title()
							else:
								if pywikibot.ImagePage(site_en, '%s-xinshu.gif' % a.title()).fileIsShared():
									warianty_obr = warianty_obr + ' | {{zch-obrazek|xt|%s|g}}' % a.title()
					
														
						if pywikibot.ImagePage(site_en, '%s-still.svg' % a.title()).fileIsShared():
							warianty_obr = warianty_obr + ' | {{zch-obrazek|st|%s}}' % a.title()
						else:
							if pywikibot.ImagePage(site_en, '%s-caoshu.svg' % a.title()).fileIsShared():
								warianty_obr = warianty_obr + ' | {{zch-obrazek|ca|%s}}' % a.title()
							else:
								if pywikibot.ImagePage(site_en, '%s-still.png' % a.title()).fileIsShared():
									warianty_obr = warianty_obr + ' | {{zch-obrazek|st|%s|p}}' % a.title()
								else:
									if pywikibot.ImagePage(site_en, '%s-caoshu.png' % a.title()).fileIsShared():
										warianty_obr = warianty_obr + ' | {{zch-obrazek|ca|%s|p}}' % a.title()
									else:
										if pywikibot.ImagePage(site_en, '%s-still.gif' % a.title()).fileIsShared():
											warianty_obr = warianty_obr + ' | {{zch-obrazek|st|%s|g}}' % a.title()
										else:
											if pywikibot.ImagePage(site_en, '%s-caoshu.gif' % a.title()).fileIsShared():
												warianty_obr = warianty_obr + ' | {{zch-obrazek|ca|%s|g}}' % a.title()

								
						if pywikibot.ImagePage(site_en, '%s-kaishu.svg' % a.title()).fileIsShared():
							warianty_obr = warianty_obr + ' | {{zch-obrazek|kt|%s}}' % a.title()
						else:
							if pywikibot.ImagePage(site_en, '%s-kaishu.png' % a.title()).fileIsShared():
								warianty_obr = warianty_obr + ' | {{zch-obrazek|kt|%s|p}}' % a.title()
							else:
								if pywikibot.ImagePage(site_en, '%s-kaishu.gif' % a.title()).fileIsShared():
									warianty_obr = warianty_obr + ' | {{zch-obrazek|kt|%s|g}}' % a.title()
												
													
						if pywikibot.ImagePage(site_en, '%s-songti.svg' % a.title()).fileIsShared():
							warianty_obr = warianty_obr + ' | {{zch-obrazek|sot|%s}}' % a.title()
						else:
							if pywikibot.ImagePage(site_en, '%s-songti.png' % a.title()).fileIsShared():
								warianty_obr = warianty_obr + ' | {{zch-obrazek|sot|%s|p}}' % a.title()
							else:
								if pywikibot.ImagePage(site_en, '%s-songti.gif' % a.title()).fileIsShared():
									warianty_obr = warianty_obr + ' | {{zch-obrazek|sot|%s|g}}' % a.title()
							

						if warianty == '{{warianty':
							tekst = tekst + '{{warianty|{{zch-w}}'
						else:
							tekst = tekst + warianty
						
						tekst = tekst + '}}'
						
						if warianty_obr != '{{warianty-obrazek':
							tekst = tekst + ' ' + warianty_obr + '}}'
						
						tekst = tekst + '\n{{kolejność}}'
					
		
						if kolejnosc_koncowa_c == '' and kolejnosc_koncowa_j == '' and kolejnosc_koncowa_t == '' and kolejnosc_koncowa_a == '':
							print('[[%s]] - na commons nie znaleziono żadnej kolejności pisania' % a.title())
							log = log + '\n*[[%s]] - na commons nie znaleziono żadnej kolejności pisania' % a.title()
						else:
							tekst = tekst + '\n'
							
						if kolejnosc_koncowa_c != '':
							tekst = tekst + '%s ' % kolejnosc_koncowa_c
						if kolejnosc_koncowa_j != '':
							tekst = tekst + '%s ' % kolejnosc_koncowa_j
						if kolejnosc_koncowa_t != '':
							tekst = tekst + '%s ' % kolejnosc_koncowa_t
						if kolejnosc_koncowa_a != '':
							tekst = tekst + '%s ' % kolejnosc_koncowa_a
					
						tekst = tekst + '\n{{znaczenia}}\n{{etymologia}}'
						
						etym = ' {{warianty-obrazek'
						if pywikibot.ImagePage(site_en, '%s-oracle.svg' % a.title()).fileIsShared():
							etym = etym + ' | {{zch-obrazek|o|%s}}' % a.title()
						else:
							if pywikibot.ImagePage(site_en, '%s-oracle.png' % a.title()).fileIsShared():
								etym = etym + ' | {{zch-obrazek|o|%s|p}}' % a.title()
								
						if pywikibot.ImagePage(site_en, '%s-bronze.svg' % a.title()).fileIsShared():
							etym = etym + ' | {{zch-obrazek|br|%s}}' % a.title()
						else:
							if pywikibot.ImagePage(site_en, '%s-bronze.png' % a.title()).fileIsShared():
								etym = etym + ' | {{zch-obrazek|br|%s|p}}' % a.title()
								
						if pywikibot.ImagePage(site_en, '%s-bigseal.svg' % a.title()).fileIsShared():
							etym = etym + ' | {{zch-obrazek|bs|%s}}' % a.title()
						else:
							if pywikibot.ImagePage(site_en, '%s-bigseal.png' % a.title()).fileIsShared():
								etym = etym + ' | {{zch-obrazek|bs|%s|p}}' % a.title()
								
						if pywikibot.ImagePage(site_en, '%s-seal.svg' % a.title()).fileIsShared():
							etym = etym + ' | {{zch-obrazek|ss|%s}}' % a.title()
						else:
							if pywikibot.ImagePage(site_en, '%s-seal.png' % a.title()).fileIsShared():
								etym = etym + ' | {{zch-obrazek|ss|%s|p}}' % a.title()
						
						etym = etym + '}}'
						
						if etym != ' {{warianty-obrazek}}':
							tekst = tekst + etym
						
						tekst = tekst + '\n{{kody|cjz='
						if canj_abort:
							print('[[%s]] - w en.wikt nie istnieje argument cjz - dodać ręcznie')
							log = log + '\n*[[%s]] - w en.wikt nie istnieje argument cjz - dodać ręcznie'
						else:
							tekst = tekst + '%s' % canj_s.group(1)
						tekst = tekst + '|cr='
						if cr_abort==1:
							print('[[%s]] - w en.wikt nie istnieje argument \'\'four\'\' - dodać ręcznie' % a.title())
							log = log + '\n*[[%s]] - w en.wikt nie istnieje argument \'\'four\'\' - dodać ręcznie' % a.title()
						else:
							tekst = tekst + '%s' % cr_s.group(1)
						tekst = tekst + '|u=%x}}' % ord(a.title())
						
						han_ref_s = re.search(han_ref, ang.get())
						if han_ref_s != None:
							tekst = tekst + '\n{{słowniki'
							
							kx_s = re.search(kx, han_ref_s.group(2))
							if kx_s != None:
								tekst = tekst + '|kx=%s' % kx_s.group(1)
							
							dkj_s = re.search(dkj, han_ref_s.group(2))
							if dkj_s != None:
								tekst = tekst + '|dkj=%s' % dkj_s.group(1)
							
							dj_s = re.search(dj, han_ref_s.group(2))
							if dj_s != None:
								tekst = tekst + '|dj=%s' % dj_s.group(1)
								
							hdz_s = re.search(hdz, han_ref_s.group(2))
							if hdz_s != None:
								tekst = tekst + '|hdz=%s' % hdz_s.group(1)
								
							tekst = tekst + '}}'
						
						tekst = tekst + '\n{{uwagi}}\n{{źródła}}\n\n'

											
					else:
						print('[[%s]] - znaleziono alternatywne zapisy, pomijam' % a.title())
						log = log + '\n*[[%s]] - znaleziono alternatywne zapisy, pomijam' % a.title()
				
					final = tekst_przed_s.group(1) + tekst + tekst_po_s.group(1)
					
					if test_mode == 1:
						print(final + '\n\n')
					else:
						a.put(final, comment = 'bot dodaje sekcję {{znak chiński}}')
				else:
					print('[[%s]] - Nie znaleziono szablonu {{Han char}}' % a.title())
					log = log + '\n*[[%s]] - Nie znaleziono szablonu {{s|Han char}}, pomijam' % a.title()
			
			log_site = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/zch/log')	
			log_stary = log_site.get()
			
			if test_mode == 1:
				print(log)
			else:
				log = log_stary + log
				log_site.put(log, comment = '%s' % a.title())
				
		
		
if __name__ == '__main__':
	try:
		main()
	finally:
		pywikibot.stopme()
