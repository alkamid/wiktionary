#!/usr/bin/python
# -*- coding: utf-8 -*-

# robienie listy haseł polskich bez wymowy

import sys
sys.path.append('/home/alkamid/wikt/pywikipedia')
#sys.path.append('/home/adam/wikt/pywikipedia')
import codecs
import catlib
import wikipedia
import pagegenerators
import re
import math
import datetime

def main():

	site = wikipedia.getSite('pl', 'wikinews')
	lista_stron = pagegenerators.AllpagesPageGenerator(site=site)
	
	re_cytat = re.compile(u'{{[cC]ytat\|(.*?)}}', re.DOTALL)
	re_tresc = re.compile(u'(.*?)($|\|2=|\|3=|\|4=|\|5=|\|[0-9]*px\|[0-9]*px\|)', re.DOTALL)
	re_autor = re.compile(u'(4=|\|[0-9]*px\|[0-9]*px\|)(.*?)($|\|)', re.DOTALL)
	re_zrodlo = re.compile(u'5=(.*)', re.DOTALL)
	
	re_cytatlewy = re.compile(u'{{[cC]ytatLewy\|(.*?)}}', re.DOTALL)
	re_cytatprawy = re.compile(u'{{[cC]ytatPrawy\|(.*?)}}', re.DOTALL)

	
	for a in lista_stron:
		log = u''
		try:
			strona = a.get()
		except wikipedia.IsRedirectPage:
			#print u'[[%s]] - przekierowanie' % a.title()
			log = log + u'\n*[[%s]] - przekierowanie' % a.title()
		except wikipedia.Error:
			print u'[[%s]] - błąd' % a.title()
			log = log + u'\n*[[%s]] - błąd' % a.title()
		else:
			
			s_cytat = re.findall(re_cytat, a.get())
			for b in s_cytat:
				final = ''
				s_tresc = re.search(re_tresc, b)
				s_autor = re.search(re_autor, b)
				s_zrodlo = re.search(re_zrodlo, b)
				print b
				print u'\n\n'
				if s_tresc:
					final = final + u'\n\'\'\'treść\'\'\': %s' % s_tresc.group(1)
					#print u'\n\'\'\'treść\'\'\': %s' % s_tresc.group(1)
				if s_autor:
					final = final + u'\n:\'\'\'autor\'\'\': %s' % (s_autor.group(2))
					print u'\n:\'\'\'autor\'\'\': %s' % (s_autor.group(2))
				if s_zrodlo:
					final = final + u'\n:\'\'\'źródło\'\'\': %s' % s_zrodlo.group(1)
					#print u'\n:\'\'\'źródło\'\'\': %s' % s_zrodlo.group(1)
				
				final = final + u'\n:\'\'\'link\'\'\': [[%s]]<br/><br/>' % a.title()
				#print u'\n:\'\'\'link\'\'\': [[%s]]<br/><br/>\n' % a.title()
				
				#print final
				file = open("output/wikinews.txt", 'a')
				file.write (final.encode("utf-8"))
				file.close
				
			s_cytatlewy = re.findall(re_cytatlewy, a.get())
			for c in s_cytatlewy:
				final_l = ''
				final_l = final_l + u'\n\'\'\'treść\'\'\': %s' % c
				final_l = final_l + u'\n:\'\'\'link\'\'\': [[%s]]<br/><br/>' % a.title()
				file = open("output/wikinews_lewy.txt", 'a')
				file.write (final_l.encode("utf-8"))
				file.close				
		
			s_cytatprawy = re.findall(re_cytatprawy, a.get())
			for d in s_cytatprawy:
				final_p = ''
				final_p = final_p + u'\n\'\'\'treść\'\'\': %s' % d
				final_p = final_p + u'\n:\'\'\'link\'\'\': [[%s]]<br/><br/>' % a.title()
				file = open("output/wikinews_prawy.txt", 'a')
				file.write (final_p.encode("utf-8"))
				file.close
					
		file = open("log/wikinews.txt", 'a')
		file.write (log.encode("utf-8"))
		file.close		
	
	

if __name__ == '__main__':
    try:
        main()
    finally:
        wikipedia.stopme()
