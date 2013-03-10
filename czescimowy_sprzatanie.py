#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import codecs
import wikipedia
import catlib
import pagegenerators
import re
import xmlreader
from klasa import *
	
def main():

	site = wikipedia.getSite()

	inp = codecs.open(u'input/czescimowy_input.txt', encoding=u'utf-8')
	
	re_spacje = re.compile(ur'\'\'(.*?)\'\'$')
	
	zamiana = []
	zamiana.append([u'\'\'rzeczownik własny, rodzaj męski\'\'', u'\'\'rzeczownik, rodzaj męski, nazwa własna\'\''])
	zamiana.append([u'\'\'rzeczownik własny, rodzaj żeński\'\'', u'\'\'rzeczownik, rodzaj żeński, nazwa własna\'\''])
	zamiana.append([u'\'\'rzeczownik własny, rodzaj nijaki\'\'', u'\'\'rzeczownik, rodzaj nijaki, nazwa własna\'\''])
	zamiana.append([u'\'\'rzeczownik, nazwa własna, rodzaj męski\'\'', u'\'\'rzeczownik, rodzaj męski, nazwa własna\'\''])
	zamiana.append([u'\'\'rzeczownik, nazwa własna, rodzaj żeński\'\'', u'\'\'rzeczownik, rodzaj żeński, nazwa własna\'\''])
	zamiana.append([u'\'\'rzeczownik, nazwa własna, rodzaj nijaki\'\'', u'\'\'rzeczownik, rodzaj nijaki, nazwa własna\'\''])
	zamiana.append([u'\'\'rzeczownik, nazwa własna, rodzaj wspólny\'\'', u'\'\'rzeczownik, rodzaj wspólny, nazwa własna\'\''])
	zamiana.append([u'\'\'związek wyrazów w funkcji rzeczownika w rodzaju nijakim, nazwa własna\'\'', u'\'\'związek wyrazów w funkcji rzeczownika rodzaju nijakiego, nazwa własna\'\''])
	zamiana.append([u'\'\'związek wyrazów w funkcji rzeczownika w rodzaju męskim, nazwa własna\'\'', u'\'\'związek wyrazów w funkcji rzeczownika rodzaju męskiego, nazwa własna\'\''])
	zamiana.append([u'\'\'związek wyrazów w funkcji rzeczownika w rodzaju żeńskim, nazwa własna\'\'', u'\'\'związek wyrazów w funkcji rzeczownika rodzaju żeńskiego, nazwa własna\'\''])
	zamiana.append([u'\'\'zaimek pytający\'\'', u'\'\'zaimek pytajny\'\''])
	zamiana.append([u'\'\'związek wyrazów w funkcji rzeczownika, rodzaj żeński\'\'', u'\'\'związek wyrazów w funkcji rzeczownika rodzaju żeńskiego\'\''])
	zamiana.append([u'\'\'związek wyrazów w funkcji rzeczownika, rodzaj męski\'\'', u'\'\'związek wyrazów w funkcji rzeczownika rodzaju męskiego\'\''])
	zamiana.append([u'\'\'związek wyrazów w funkcji rzeczownika, rodzaj nijaki\'\'', u'\'\'związek wyrazów w funkcji rzeczownika rodzaju nijakiego\'\''])
	zamiana.append([u'\'\'związek wyrazów w funkcji rzeczownika, rodzaj żeński, nazwa własna\'\'', u'\'\'związek wyrazów w funkcji rzeczownika rodzaju żeńskiego, nazwa własna\'\''])
	zamiana.append([u'\'\'związek wyrazów w funkcji rzeczownika, rodzaj męski, nazwa własna\'\'', u'\'\'związek wyrazów w funkcji rzeczownika rodzaju męskiego, nazwa własna\'\''])
	zamiana.append([u'\'\'związek wyrazów w funkcji rzeczownika, rodzaj nijaki, nazwa własna\'\'', u'\'\'związek wyrazów w funkcji rzeczownika rodzaju nijakiego, nazwa własna\'\''])
	#zamiana.append([u'\'\'rzeczownik, rodzaj żeński i męski\'\'', u'\'\'rzeczownik, rodzaj męski lub żeński\'\''])
	#zamiana.append([u'\'\'rzeczownik, rodzaj męski i żeński\'\'', u'\'\'rzeczownik, rodzaj męski lub żeński\'\''])
	zamiana.append([u'\'\'rzeczownik, rodzaj żeński lub męski\'\'', u'\'\'rzeczownik, rodzaj męski lub żeński\'\''])
	
	for a in zamiana:
		print u'|-\n|%s\n|%s' % (a[0], a[1])
	
	for line in inp:
		try: h = Haslo(line)
		except sectionsNotFound:
			continue
		else:
			for c in h.listLangs:
				c.pola()
				if c.type != 11 and c.type != 2 and c.type != 3 and c.type != 4 and c.type != 7:
					
					for d in c.znaczeniaDetail:
						s_spacje = re.search(re_spacje, d[0])
						if s_spacje:
							d[0] = u'\'\'%s\'\'' % (s_spacje.group(1).strip())
							c.saveChanges()
						for zm in zamiana:
							if d[0] == zm[0]:
								d[0] = d[0].replace(zm[0], zm[1])
								c.saveChanges()
						

			h.push(False, u'Porządkowanie nagłówków sekcji znaczenia')


if __name__ == '__main__':
	try:
		main()
	finally:
		wikipedia.stopme()
