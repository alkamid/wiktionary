#!/usr/bin/python
# -*- coding: utf-8 -*-

import wikipedia
import pagegenerators
import re
import xmlreader
import collections
from klasa import *


# the script looks for newly added languages (the languages for which the templates do not exist)	
def missingLangs(data):

	data_slownie = data[6] + data[7] + u'.' + data[4] + data[5] + u'.' + data[0] + data[1] + data[2] + data[3]
	lista_stron = list(getListFromXML(data))
	wikt = wikipedia.Site('pl', 'wiktionary')
	foundList = set()
	notFound = set()
	
	LangsMediaWiki = getAllLanguages()

	for a in lista_stron:

		try: word = Haslo(a.title, a.text)
		except notFromMainNamespace:
			pass
		except sectionsNotFound:
			pass
		except WrongHeader:
			pass
		else:
			if word.type == 3:
				for lang in word.listLangs:
					if lang.type != 2:
						if lang.lang not in foundList:
							foundList.add(lang.lang)
				
	existing = set(a.shortName for a in LangsMediaWiki)
	diff = foundList - existing

	for a in lista_stron:
		try: word = Haslo(a.title, a.text)
		except notFromMainNamespace:
			pass
		except sectionsNotFound:
			pass
		except WrongHeader:
			pass
		else:
			if word.type == 3:
				for lang in word.listLangs:
					if lang.type != 2:
						if lang.lang in diff:
							print u'%s - %s' % (lang.lang, word.title)