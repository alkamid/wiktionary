#!/usr/bin/python
# -*- coding: utf-8 -*-

# szuka danego przez szukany_tekst wyrażenia w hasłach

import codecs
import catlib
import wikipedia
import pagegenerators
import re
import xmlreader
import datetime
import time
from klasa import *

def meanings():

	global data
	data = '20110512'
	#lista_stron1 = xmlreader.XmlDump('plwiktionary-%s-pages-articles.xml' % data)
	
	
	site_en = wikipedia.Site('en', 'wiktionary')
	commons = wikipedia.Site('commons', 'commons')
	
	try: wikipedia.ImagePage(site_en, u'File:Hacienda Chac, Yucatán (02).JPG').fileIsOnCommons()
	except wikipedia.NoPage:
		pass
	except wikipedia.IsRedirectPage:
		pass
	else:
		try: tmpget = wikipedia.ImagePage(commons, u'File:Hacienda Chac, Yucatán (02).JPG').get()
		except wikipedia.NoPage or wikipedia.IsRedirectPage:
			pass
		except wikipedia.IsRedirectPage:
			pass
		else:
			if not '{{ARlicense' in tmpget:
				print 'hop'
	
	
if __name__ == '__main__':
    try:
        meanings()
    finally:
        wikipedia.stopme()
