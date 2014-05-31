#!/usr/bin/python
# -*- coding: utf-8 -*-

# szuka danego przez szukany_tekst wyrażenia w hasłach

import codecs
from pywikibot import Category
import pywikibot
from pywikibot import pagegenerators
import re
from pywikibot import xmlreader
import datetime
import time
from klasa import *

def meanings():

	global data
	data = '20110512'
	#lista_stron1 = xmlreader.XmlDump('plwiktionary-%s-pages-articles.xml' % data)
	print 'hohoho'
	file = open('output/ttt.txt', 'w')
	file.write('aaa'.encode( "utf-8" ))
	file.close
	
	site_en = pywikibot.Site('en', 'wiktionary')
	commons = pywikibot.Site('commons', 'commons')
	
	try: pywikibot.ImagePage(site_en, u'File:Hacienda Chac, Yucatán (02).JPG').fileIsShared()
	except pywikibot.NoPage:
		pass
	except pywikibot.IsRedirectPage:
		pass
	else:
		try: tmpget = pywikibot.ImagePage(commons, u'File:Hacienda Chac, Yucatán (02).JPG').get()
		except pywikibot.NoPage or pywikibot.IsRedirectPage:
			pass
		except pywikibot.IsRedirectPage:
			pass
		else:
			if not '{{ARlicense' in tmpget:
				print 'hop'
	
	
if __name__ == '__main__':
    try:
        meanings()
    finally:
        pywikibot.stopme()
