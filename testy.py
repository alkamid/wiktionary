#!/usr/bin/python
# -*- coding: utf-8 -*-

from statystyka import *
import klasa

def test(haslo):
        
        lista_stron2 = haslo
	for a in lista_stron2:
                print(a)
		#if (i<1000):
                try: haslo = klasa.Haslo(a)
                except sectionsNotFound:
                        pass
                except WrongHeader:
                        pass
                else:
                        if haslo.type != 5:
                                for b in haslo.listLangs:
                                        #print haslo.title
                                        if b.type != 2 and b.type != 3:
                                                if b.langLong == 'termin obcy w języku polskim':
                                                        b.langLong = 'język polski'
                                                b.pola()
                                                if not b.inflectedOnly:
                                                        print((countLength(b.content)))
        

def testNew(haslo):

        temps = deletedTemplates()

        lista_stron2 = haslo
	for a in lista_stron2:
		#if (i<1000):
                try: haslo = klasa.Haslo(a)
                except sectionsNotFound:
                        pass
                except WrongHeader:
                        pass
                else:
                        if haslo.type != 5:
                                for b in haslo.listLangs:
                                        #print haslo.title
                                        if b.type != 2 and b.type != 3:
                                                if b.langLong == 'termin obcy w języku polskim':
                                                        b.langLong = 'język polski'
                                                b.pola()
                                                if not b.inflectedOnly:
                                                        #print b.content
                                                        print((countLength(b.content, temps)))


#word = [u'gaciara', u'gacić', u'gąbka', u'galant', u'gargantuizm']
word = ['poniedziałek', 'gacić', 'gargantuizm']
word = ['galaktyka']

testNew(word)
#test(word)
