#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
#sys.path.append('/home/adam/pywiki/pywikipedia')
sys.path.append('/home/alkamid/wikt/pywikipedia')
import wikipedia
import catlib
import pagegenerators
import re

def main():
	test_mode = 0;
	site = wikipedia.getSite()
	site_en = wikipedia.getSite('en', 'wiktionary')
	site_com = wikipedia.getSite('commons', 'commons')
	cat = catlib.Category(site,u'Kategoria:chiński standardowy (indeks)')
	cat_com = catlib.Category(site, u'Chinese kanji stroke order')
	lista_stron = pagegenerators.CategorizedPageGenerator(cat)
	lista_com = pagegenerators.CategorizedPageGenerator(cat_com)
	log_site = wikipedia.Page(site, u'Wikipedysta:AlkamidBot/zch/log')
	
	lista = []
	istnieje = []
	
	han_char = re.compile(u'{{Han(_| )char\|(.*?)}')
	han_ref = re.compile(u'{{Han(_| )ref\|(.*})')
	zh_f = re.compile(u'{{zh-forms\|(.*)}')
	jap_f = re.compile(u'{{ja-forms\|(.*)}')
	kx = re.compile(u'kx=(.*?)(\||})')
	dkj = re.compile(u'\|dkj=(.*?)(\||})')
	dj = re.compile(u'\|dj=(.*?)(\||})')
	hdz = re.compile(u'\|hdz=(.*?)(\||})')
	rn = re.compile(u'rn=([0-9]*?)\|')
	rad = re.compile(u'rad=(.)')
	han_as = re.compile(u'as=([0-9]*?)\|')
	sn = re.compile(u'sn=([0-9]*?)\|')
	canj = re.compile(u'canj=([^\|]*)')
	cr = re.compile(u'four=(.*?)\|')
	alt = re.compile(u'alt=(.*?)\|')
	asj = re.compile(u'asj=(.*?)\|')
	tekst_przed = re.compile(u'(.*?)=', re.DOTALL)
	tekst_po = re.compile(u'.*?(=.*)', re.DOTALL)
	grafika = re.compile(u'(\-bw\.|\-red\.|\-order\.|{{zch\-cienie}}|{{zch\-animacja}}|{{zch\-komiks}})')
	
	for page in lista_stron:
		if len(page.title())==1:
			lista.append(page)
	
		
	for a in lista:
		tekst = u''
		
		rn_abort = 0
		rad_abort = 0
		han_as_abort = 0
		sn_abort = 0
		canj_abort = 0
		cr_abort = 0
		
		try:
			strona = a.get()
		except wikipedia.IsRedirectPage:
			print u'[[%s]] - przekierowanie' % a.title()
			log = log + u'\n*[[%s]] - przekierowanie' % a.title()
		except wikipedia.Error:
			print u'[[%s]] - błąd' % a.title()
			log = log + u'\n*[[%s]] - błąd' % a.title()
		else:
			
			tekst_przed_s = re.search(tekst_przed, a.get())
			tekst_po_s = re.search(tekst_po, a.get())
			
			log = u''
			
			if test_mode == 1:
				sekcja_znak = u'fdssagrefadf'
			else:
				sekcja_znak = u'{{znak chiński}}'
			
			if sekcja_znak in a.get():
				print u'[[%s]] - istnieje już sekcja {{znak chiński}}' % a.title()
				log = log + u'\n*[[%s]] - istnieje już sekcja {{s|znak chiński}}' % a.title()
				istnieje.append(a)
			else:
				ang = wikipedia.Page(site_en, a.title())
				han_char_s = re.search(han_char, ang.get())
			
				grafika_s = re.search(grafika, a.get())
				if grafika_s != None:
					print u'[[%s]] - znaleziono grafikę z CJK stroke order' % a.title()
					log = log + u'\n*[[%s]] - znaleziono grafikę z CJK stroke order' % a.title()
			
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
						if alt_s.group(1) == u'':
							alter = 0
						else:
							alter = 1
					if asj_s == None:
						alter1 = 0
					else:
						if asj_s.group(1) == u'':
							alter1 = 0
						else:
							alter1 = 1
						
					if alter == 0 and alter1 == 0:			
				
						#print a.title()
						if rn_s == None:
							print u'[[%s]] - Nie istnieje argument \'rn\'' % a.title()
							log = log + u'\n*[[%s]] - Nie istnieje argument \'rn\'' % a.title()
							rn_abort = 1
						if rad_s == None:
							print u'[[%s]] - Nie istnieje argument \'rad\'' % a.title()
							log = log + u'\n*[[%s]] - Nie istnieje argument \'rad\'' % a.title()
							rad_abort = 1
						if han_as_s != None:
							#print han_as_s.group(1)
							if han_as_s.group(1) == u'0' or han_as_s.group(1) ==u'00':
								as_output = u'+ 0'
							else:
								if han_as_s.group(1)[0] == u'0':
									as_output = u'+ %s' % han_as_s.group(1)[1]
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
							if cr_s.group(1).isspace() or cr_s.group(1) == u'':
								print u'[[%s]] - argument \'four\' na en.wikt jest pusty - dodać ręcznie' % a.title()
								log = log + u'\n*[[%s]] - argument \'four\' na en.wikt jest pusty - dodać ręcznie' % a.title()
						else:
							cr_abort = 1
				
						kolejnosc_koncowa_c = u''
						
						if wikipedia.ImagePage(site_en, u'%s-bw.png' % a.title()).fileIsOnCommons():
							kolejnosc_koncowa_c = u'{{zch-komiks}}'
						else:
							if wikipedia.ImagePage(site_en, u'%s-red.png' % a.title()).fileIsOnCommons():
								kolejnosc_koncowa_c = u'{{zch-cienie}}'
							else:
								if wikipedia.ImagePage(site_en, u'%s-order.gif' % a.title()).fileIsOnCommons():
									kolejnosc_koncowa_c = u'{{zch-animacja}}'

						
						kolejnosc_koncowa_j = u''
						
						if wikipedia.ImagePage(site_en, u'%s-jbw.png' % a.title()).fileIsOnCommons():
							kolejnosc_koncowa_j = u'{{zch-komiks|j}}'
						else:
							if wikipedia.ImagePage(site_en, u'%s-jred.png' % a.title()).fileIsOnCommons():
								kolejnosc_koncowa_j = u'{{zch-cienie|j}}'
							else:
								if wikipedia.ImagePage(site_en, u'%s-jorder.gif' % a.title()).fileIsOnCommons():
									kolejnosc_koncowa_j = u'{{zch-animacja|j}}'

						
						kolejnosc_koncowa_t = u''
						
						if wikipedia.ImagePage(site_en, u'%s-tbw.png' % a.title()).fileIsOnCommons():
							kolejnosc_koncowa_t = u'{{zch-komiks|t}}'
						else:
							if wikipedia.ImagePage(site_en, u'%s-tred.png' % a.title()).fileIsOnCommons():
								kolejnosc_koncowa_t = u'{{zch-cienie|t}}'
							else:
								if wikipedia.ImagePage(site_en, u'%s-torder.gif' % a.title()).fileIsOnCommons():
									kolejnosc_koncowa_t = u'{{zch-animacja|t}}'
								
									
						kolejnosc_koncowa_a = u''
						
						if wikipedia.ImagePage(site_en, u'%s-abw.png' % a.title()).fileIsOnCommons():
							kolejnosc_koncowa_a = u'{{zch-komiks|a}}'
						else:
							if wikipedia.ImagePage(site_en, u'%s-ared.png' % a.title()).fileIsOnCommons():
								kolejnosc_koncowa_a = u'{{zch-cienie|a}}'
							else:
								if wikipedia.ImagePage(site_en, u'%s-aorder.gif' % a.title()).fileIsOnCommons():
									kolejnosc_koncowa_a = u'{{zch-animacja|a}}'
						
																						
						tekst = u'== {{zh|%s}} ({{znak chiński}}) ==\n{{klucz}}' % a.title()	
					
						if rn_abort or rad_abort or han_as_abort:
							print u'[[%s]] - w en.wikt nie istnieje któryś z argumentów do {{klucz}} - dodać ręcznie' % a.title()
							log = log + u'\n*[[%s]] - w en.wikt nie istnieje któryś z argumentów do {{s|klucz}} - dodać ręcznie' % a.title()
						else:
							tekst = tekst + u' %s %s %s' % (rn_s.group(1), rad_s.group(1), as_output)
					
						tekst = tekst + u'\n{{kreski}}'
						if sn_abort:
							print u'[[%s]] - w en.wikt nie istnieje argument do {{kreski}} - dodać ręcznie'
							log = log + u'\n*[[%s]] - w en.wikt nie istnieje argument do {{s|kreski}} - dodać ręcznie'
						else:
							tekst = tekst + u' %s\n' % sn_s.group(1)
						
						zh_f_s = re.search(zh_f, ang.get())	
						ja_f_s = re.search(jap_f, ang.get())
						
						warianty = u'{{warianty'
						warianty_obr = u'{{warianty-obrazek'
						ku = u''
						xu = u''
						sou = u''
						sot = u''
						ming = u''
						upr = u''
						trad = u''
						shin = u''
						
						
						if zh_f_s != None:
							zh_f_str = zh_f_s.group(1).replace("[","").replace("]","").replace("{{zh-lookup|", "").replace("}", "")
							zh_osobno = zh_f_str.split('|')
							warianty = warianty + u' | {{zch-w|ct|%s}} | {{zch-w|cu|%s}}' % (zh_osobno[1], zh_osobno[0])

							'''
							if wikipedia.ImagePage(site_en, u'%s-kaishu.svg' % zh_osobno[0]).fileIsOnCommons():
								ku = u' | {{zch-obrazek|ku|%s}}' % zh_osobno[0]
							else:
								if wikipedia.ImagePage(site_en, u'%s-kaishu.png' % zh_osobno[0]).fileIsOnCommons():
									ku = u' | {{zch-obrazek|ku|%s|p}}' % zh_osobno[0]
								else:
									if wikipedia.ImagePage(site_en, u'%s-kaishu.gif' % zh_osobno[0]).fileIsOnCommons():
										ku = u' | {{zch-obrazek|ku|%s|g}}' % zh_osobno[0]
						
							if wikipedia.ImagePage(site_en, u'%s-xinshu.svg' % zh_osobno[0]).fileIsOnCommons():
								xu = u' | {{zch-obrazek|xu|%s}}' % zh_osobno[0]
							else:
								if wikipedia.ImagePage(site_en, u'%s-xinshu.png' % zh_osobno[0]).fileIsOnCommons():
									xu = u' | {{zch-obrazek|xu|%s|p}}' % zh_osobno[0]
								else:
									if wikipedia.ImagePage(site_en, u'%s-xinshu.gif' % zh_osobno[0]).fileIsOnCommons():
										xu = u' | {{zch-obrazek|xu|%s|g}}' % zh_osobno[0]

							if wikipedia.ImagePage(site_en, u'%s-songti.svg' % zh_osobno[0]).fileIsOnCommons():
								sou = u' | {{zch-obrazek|sou|%s}}' % zh_osobno[0]
							else:
								if wikipedia.ImagePage(site_en, u'%s-songti.png' % zh_osobno[0]).fileIsOnCommons():
									sou = u' | {{zch-obrazek|sou|%s|p}}' % zh_osobno[0]
								else:
									if wikipedia.ImagePage(site_en, u'%s-songti.gif' % zh_osobno[0]).fileIsOnCommons():
										sou = u' | {{zch-obrazek|sou|%s|g}}' % zh_osobno[0]
							
							if ku != u'' or xu !=u'' or sou !=u'':
								warianty = warianty + u'{{warianty-obrazek'
								if ku != u'':
									warianty = warianty + ku
								if xu !=u'':
									warianty = warianty + xu
								if sou !=u'':
									warianty = warianty + sou
								warianty = warianty + u'}}'
								'''
							
						if ja_f_s != None:
							ja_f_str = ja_f_s.group(1).replace("[","").replace("]","").replace("{{zh-lookup|", "").replace("}", "")
							ja_osobno = ja_f_str.split('|')
							warianty = warianty + u' | {{zch-w|js|%s}} | {{zch-w|ct|%s}} | {{zch-w|cu|%s}}' % (ja_osobno[0], ja_osobno[2], ja_osobno[1])
							trad = ja_osobno[2]
							upr = ja_osobno[1]
							shin = ja_osobno[0]							
							
							'''if wikipedia.ImagePage(site_en, u'%s-kaishu.svg' % ja_osobno[1]).fileIsOnCommons():
								ku = u' | {{zch-obrazek|ku|%s}}' % ja_osobno[1]
							else:
								if wikipedia.ImagePage(site_en, u'%s-kaishu.png' % ja_osobno[1]).fileIsOnCommons():
									ku = u' | {{zch-obrazek|ku|%s|p}}' % ja_osobno[1]
								else:
									if wikipedia.ImagePage(site_en, u'%s-kaishu.gif' % ja_osobno[1]).fileIsOnCommons():
										ku = u' | {{zch-obrazek|ku|%s|g}}' % ja_osobno[1]
						
							if wikipedia.ImagePage(site_en, u'%s-xinshu.svg' % ja_osobno[1]).fileIsOnCommons():
								xu = u' | {{zch-obrazek|xu|%s}}' % ja_osobno[1]
							else:
								if wikipedia.ImagePage(site_en, u'%s-xinshu.png' % ja_osobno[1]).fileIsOnCommons():
									xu = u' | {{zch-obrazek|xu|%s|p}}' % ja_osobno[1]
								else:
									if wikipedia.ImagePage(site_en, u'%s-xinshu.gif' % ja_osobno[1]).fileIsOnCommons():
										xu = u' | {{zch-obrazek|xu|%s|g}}' % ja_osobno[1]

							if wikipedia.ImagePage(site_en, u'%s-songti.svg' % ja_osobno[1]).fileIsOnCommons():
								sou = u' | {{zch-obrazek|sou|%s}}' % ja_osobno[1]
							else:
								if wikipedia.ImagePage(site_en, u'%s-songti.png' % ja_osobno[1]).fileIsOnCommons():
									sou = u' | {{zch-obrazek|sou|%s|p}}' % ja_osobno[1]
								else:
									if wikipedia.ImagePage(site_en, u'%s-songti.gif' % ja_osobno[1]).fileIsOnCommons():
										sou = u' | {{zch-obrazek|sou|%s|g}}' % ja_osobno[1]
							
							if ku != u'' or xu !=u'' or sou !=u'':
								warianty = warianty + u'{{warianty-obrazek'
								if ku != u'':
									warianty = warianty + ku
								if xu !=u'':
									warianty = warianty + xu
								if sou !=u'':
									warianty = warianty + sou
								warianty = warianty + u'}}'''

						
						
						if wikipedia.ImagePage(site_en, u'%s-clerical.svg' % a.title()).fileIsOnCommons():
							warianty_obr = warianty_obr + u' | {{zch-obrazek|c|%s}}' % a.title()
						else:
							if wikipedia.ImagePage(site_en, u'%s-clerical.png' % a.title()).fileIsOnCommons():
								warianty_obr = warianty_obr + u' | {{zch-obrazek|c|%s|p}}' % a.title()
							else:
								if wikipedia.ImagePage(site_en, u'%s-clerical.gif' % a.title()).fileIsOnCommons():
									warianty_obr = warianty_obr + u' | {{zch-obrazek|c|%s|g}}' % a.title()
				
					
					
						if wikipedia.ImagePage(site_en, u'%s-xinshu.svg' % a.title()).fileIsOnCommons():
							warianty_obr = warianty_obr + u' | {{zch-obrazek|xt|%s}}' % a.title()
						else:
							if wikipedia.ImagePage(site_en, u'%s-xinshu.png' % a.title()).fileIsOnCommons():
								warianty_obr = warianty_obr + u' | {{zch-obrazek|xt|%s|p}}' % a.title()
							else:
								if wikipedia.ImagePage(site_en, u'%s-xinshu.gif' % a.title()).fileIsOnCommons():
									warianty_obr = warianty_obr + u' | {{zch-obrazek|xt|%s|g}}' % a.title()
					
														
						if wikipedia.ImagePage(site_en, u'%s-still.svg' % a.title()).fileIsOnCommons():
							warianty_obr = warianty_obr + u' | {{zch-obrazek|st|%s}}' % a.title()
						else:
							if wikipedia.ImagePage(site_en, u'%s-caoshu.svg' % a.title()).fileIsOnCommons():
								warianty_obr = warianty_obr + u' | {{zch-obrazek|ca|%s}}' % a.title()
							else:
								if wikipedia.ImagePage(site_en, u'%s-still.png' % a.title()).fileIsOnCommons():
									warianty_obr = warianty_obr + u' | {{zch-obrazek|st|%s|p}}' % a.title()
								else:
									if wikipedia.ImagePage(site_en, u'%s-caoshu.png' % a.title()).fileIsOnCommons():
										warianty_obr = warianty_obr + u' | {{zch-obrazek|ca|%s|p}}' % a.title()
									else:
										if wikipedia.ImagePage(site_en, u'%s-still.gif' % a.title()).fileIsOnCommons():
											warianty_obr = warianty_obr + u' | {{zch-obrazek|st|%s|g}}' % a.title()
										else:
											if wikipedia.ImagePage(site_en, u'%s-caoshu.gif' % a.title()).fileIsOnCommons():
												warianty_obr = warianty_obr + u' | {{zch-obrazek|ca|%s|g}}' % a.title()

								
						if wikipedia.ImagePage(site_en, u'%s-kaishu.svg' % a.title()).fileIsOnCommons():
							warianty_obr = warianty_obr + u' | {{zch-obrazek|kt|%s}}' % a.title()
						else:
							if wikipedia.ImagePage(site_en, u'%s-kaishu.png' % a.title()).fileIsOnCommons():
								warianty_obr = warianty_obr + u' | {{zch-obrazek|kt|%s|p}}' % a.title()
							else:
								if wikipedia.ImagePage(site_en, u'%s-kaishu.gif' % a.title()).fileIsOnCommons():
									warianty_obr = warianty_obr + u' | {{zch-obrazek|kt|%s|g}}' % a.title()
												
													
						if wikipedia.ImagePage(site_en, u'%s-songti.svg' % a.title()).fileIsOnCommons():
							warianty_obr = warianty_obr + u' | {{zch-obrazek|sot|%s}}' % a.title()
						else:
							if wikipedia.ImagePage(site_en, u'%s-songti.png' % a.title()).fileIsOnCommons():
								warianty_obr = warianty_obr + u' | {{zch-obrazek|sot|%s|p}}' % a.title()
							else:
								if wikipedia.ImagePage(site_en, u'%s-songti.gif' % a.title()).fileIsOnCommons():
									warianty_obr = warianty_obr + u' | {{zch-obrazek|sot|%s|g}}' % a.title()
					
						
						'''if sot != u'':
							ming = ming + sot
						else:
							if zh_f_s != None:
								ming = ming + u' | {{zch-w|ct|%s}}' % zh_osobno[1]
							if ja_f_s != None:
								ming = ming + u' | {{zch-w|ct|%s}}' % ja_osobno[2]		

						if sou != u'':
							ming = ming + sou
						else:
							if zh_f_s != None:
								ming = ming + u' | {{zch-w|cu|%s}}' % zh_osobno[0]
							if ja_f_s != None:
								ming = ming + u' | {{zch-w|cu|%s}}' % ja_osobno[1]'''
							

						if warianty == u'{{warianty':
							tekst = tekst + u'{{warianty|{{zch-w}}'
						else:
							tekst = tekst + warianty
						
						tekst = tekst + u'}}'
						
						if warianty_obr != u'{{warianty-obrazek':
							tekst = tekst + u' ' + warianty_obr + u'}}'
						
						tekst = tekst + u'\n{{kolejność}}'
					
		
						if kolejnosc_koncowa_c == u'' and kolejnosc_koncowa_j == u'' and kolejnosc_koncowa_t == u'' and kolejnosc_koncowa_a == u'':
							print u'[[%s]] - na commons nie znaleziono żadnej kolejności pisania' % a.title()
							log = log + u'\n*[[%s]] - na commons nie znaleziono żadnej kolejności pisania' % a.title()
						else:
							tekst = tekst + u'\n'
							
						if kolejnosc_koncowa_c != u'':
							tekst = tekst + u'%s ' % kolejnosc_koncowa_c
						if kolejnosc_koncowa_j != u'':
							tekst = tekst + u'%s ' % kolejnosc_koncowa_j
						if kolejnosc_koncowa_t != u'':
							tekst = tekst + u'%s ' % kolejnosc_koncowa_t
						if kolejnosc_koncowa_a != u'':
							tekst = tekst + u'%s ' % kolejnosc_koncowa_a
					
						tekst = tekst + u'\n{{znaczenia}}\n{{etymologia}}'
						
						etym = u' {{warianty-obrazek'
						if wikipedia.ImagePage(site_en, u'%s-oracle.svg' % a.title()).fileIsOnCommons():
							etym = etym + u' | {{zch-obrazek|o|%s}}' % a.title()
						else:
							if wikipedia.ImagePage(site_en, u'%s-oracle.png' % a.title()).fileIsOnCommons():
								etym = etym + u' | {{zch-obrazek|o|%s|p}}' % a.title()
								
						if wikipedia.ImagePage(site_en, u'%s-bronze.svg' % a.title()).fileIsOnCommons():
							etym = etym + u' | {{zch-obrazek|br|%s}}' % a.title()
						else:
							if wikipedia.ImagePage(site_en, u'%s-bronze.png' % a.title()).fileIsOnCommons():
								etym = etym + u' | {{zch-obrazek|br|%s|p}}' % a.title()
								
						if wikipedia.ImagePage(site_en, u'%s-bigseal.svg' % a.title()).fileIsOnCommons():
							etym = etym + u' | {{zch-obrazek|bs|%s}}' % a.title()
						else:
							if wikipedia.ImagePage(site_en, u'%s-bigseal.png' % a.title()).fileIsOnCommons():
								etym = etym + u' | {{zch-obrazek|bs|%s|p}}' % a.title()
								
						if wikipedia.ImagePage(site_en, u'%s-seal.svg' % a.title()).fileIsOnCommons():
							etym = etym + u' | {{zch-obrazek|ss|%s}}' % a.title()
						else:
							if wikipedia.ImagePage(site_en, u'%s-seal.png' % a.title()).fileIsOnCommons():
								etym = etym + u' | {{zch-obrazek|ss|%s|p}}' % a.title()
						
						etym = etym + u'}}'
						
						if etym != u' {{warianty-obrazek}}':
							tekst = tekst + etym
						
						tekst = tekst + '\n{{kody|cjz='
						if canj_abort:
							print u'[[%s]] - w en.wikt nie istnieje argument cjz - dodać ręcznie'
							log = log + u'\n*[[%s]] - w en.wikt nie istnieje argument cjz - dodać ręcznie'
						else:
							tekst = tekst + u'%s' % canj_s.group(1)
						tekst = tekst + u'|cr='
						if cr_abort==1:
							print u'[[%s]] - w en.wikt nie istnieje argument \'\'four\'\' - dodać ręcznie' % a.title()
							log = log + u'\n*[[%s]] - w en.wikt nie istnieje argument \'\'four\'\' - dodać ręcznie' % a.title()
						else:
							tekst = tekst + '%s' % cr_s.group(1)
						tekst = tekst + u'|u=%x}}' % ord(a.title())
						
						han_ref_s = re.search(han_ref, ang.get())
						if han_ref_s != None:
							tekst = tekst + u'\n{{słowniki'
							
							kx_s = re.search(kx, han_ref_s.group(2))
							if kx_s != None:
								tekst = tekst + u'|kx=%s' % kx_s.group(1)
							
							dkj_s = re.search(dkj, han_ref_s.group(2))
							if dkj_s != None:
								tekst = tekst + u'|dkj=%s' % dkj_s.group(1)
							
							dj_s = re.search(dj, han_ref_s.group(2))
							if dj_s != None:
								tekst = tekst + u'|dj=%s' % dj_s.group(1)
								
							hdz_s = re.search(hdz, han_ref_s.group(2))
							if hdz_s != None:
								tekst = tekst + u'|hdz=%s' % hdz_s.group(1)
								
							tekst = tekst + u'}}'
						
						tekst = tekst + u'\n{{uwagi}}\n{{źródła}}\n\n'

											
					else:
						print u'[[%s]] - znaleziono alternatywne zapisy, pomijam' % a.title()
						log = log + u'\n*[[%s]] - znaleziono alternatywne zapisy, pomijam' % a.title()
				
					final = tekst_przed_s.group(1) + tekst + tekst_po_s.group(1)
					
					if test_mode == 1:
						print final + '\n\n'
					else:
						a.put(final, comment = u'bot dodaje sekcję {{znak chiński}}')
				else:
					print u'[[%s]] - Nie znaleziono szablonu {{Han char}}' % a.title()
					log = log + u'\n*[[%s]] - Nie znaleziono szablonu {{s|Han char}}, pomijam' % a.title()
			
			log_site = wikipedia.Page(site, u'Wikipedysta:AlkamidBot/zch/log')	
			log_stary = log_site.get()
			
			if test_mode == 1:
				print log
			else:
				log = log_stary + log
				log_site.put(log, comment = u'%s' % a.title())
				
		
		
if __name__ == '__main__':
	try:
		main()
	finally:
		wikipedia.stopme()
