#!/usr/bin/python
# -*- coding: utf-8 -*-

# szuka danego przez szukany_tekst wyrażenia w hasłach

import codecs
from pywikibot import Category
import pywikibot
from pywikibot import pagegenerators
import re
from pywikibot import xmlreader
from klasa import *

def main():
	
	data = '20111102'
	
	lista_stron1 = xmlreader.XmlDump('/mnt/user-store/dumps/plwiktionary/plwiktionary-%s-pages-articles.xml' % data)	
	lista_stron2 = xmlreader.XmlDump.parse(lista_stron1)
	text = ''
	
	tempLangs = []
	
	notFound = []
	notFoundList = collections.defaultdict(list)
	
	LangsMediaWiki = getAllLanguages()
	
	for a in lista_stron2:
		try: word = Haslo(a.title, a.text)
		except sectionsNotFound:
			pass
		else:
			if word.type == 3:
				for lang in word.listLangs:
					if lang.type != 2:
						lang.pola()
						if lang.type == 1 and lang.znaczeniaDetail:
							for d in lang.znaczeniaDetail:
								if '{{lm}} od' in d[1] or 'liczba mnoga od' in d[1] or 'zwykle w {{lm}}' in d[1] or 'zwykle w liczbie mnogiej' in d[1] or 'w {{lm}}' in d[1] or 'w liczbie mnogiej' in d[1] or 'l.m.' in d[1]:
									notFoundList['%s' % lang.lang].append(word.title)
													
	for a in LangsMediaWiki:
		if notFoundList['%s' % a.shortName] and a.shortName:
			text += '== %s ==' % (a.longName)
			for b in notFoundList['%s' % a.shortName]:
				text += '\n*[[%s]]' % (b)
			text += '\n'

	file = open('output/liczba_mnoga.txt', 'w')
	file.write(text.encode( "utf-8" ))
	file.close
			
if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
