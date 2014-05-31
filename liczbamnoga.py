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
	
	data = u'20111102'
	
	lista_stron1 = xmlreader.XmlDump('/mnt/user-store/dumps/plwiktionary/plwiktionary-%s-pages-articles.xml' % data)	
	lista_stron2 = xmlreader.XmlDump.parse(lista_stron1)
	text = u''
	
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
								if u'{{lm}} od' in d[1] or u'liczba mnoga od' in d[1] or u'zwykle w {{lm}}' in d[1] or u'zwykle w liczbie mnogiej' in d[1] or u'w {{lm}}' in d[1] or u'w liczbie mnogiej' in d[1] or u'l.m.' in d[1]:
									notFoundList[u'%s' % lang.lang].append(word.title)
													
	for a in LangsMediaWiki:
		if notFoundList[u'%s' % a.shortName] and a.shortName:
			text += u'== %s ==' % (a.longName)
			for b in notFoundList[u'%s' % a.shortName]:
				text += u'\n*[[%s]]' % (b)
			text += u'\n'

	file = open('output/liczba_mnoga.txt', 'w')
	file.write(text.encode( "utf-8" ))
	file.close
			
if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
