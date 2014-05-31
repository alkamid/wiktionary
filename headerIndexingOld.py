#!/usr/bin/python
# -*- coding: utf-8 -*-

# wstawia odpowiedni parametr w językach używających znaków diaktrycznych

import codecs
from pywikibot import Category
import pywikibot
from pywikibot import pagegenerators
import re
from klasa import *

def main():
    site = pywikibot.getSite()
    
    replace = {}
    replace[u'nowogrecki'] = {u'Ά': u'Α', u'Έ': u'Ε', u'Ί': u'Ι', u'Ϊ': u'Ι', u'Ό': u'Ο', u'Ύ': u'Υ', u'Ϋ': u'Υ', u'Ώ': u'Ω', u'ά': u'α', u'έ': u'ε', u'ί': u'ι', u'ϊ': u'ι', u'ΐ': u'ι', u'ό': u'ο', u'ύ': u'υ', u'ϋ': u'υ', u'ΰ': u'υ', u'ώ': u'ω', u'ς': u'σ'}
    replace[u'francuski'] = {u'À': u'A', u'Â': u'A', u'Ç': u'C', u'É': u'E', u'È': u'E', u'Ë': u'E', u'Ê': u'E', u'Î': u'I', u'Ï': u'I', u'Ô': u'O', u'Œ': u'OE', u'Ù': u'U', u'Ú': u'U', u'Û': u'U', u'à': u'a', u'â': u'a', u'ç': u'c', u'é': u'e', u'è': u'e', u'ë': u'e', u'ê': u'e', u'î': u'i', u'ï': u'i', u'ô': u'o', u'œ': u'oe', u'ù': u'u', u'ú': u'u', u'û': u'u'}
    replace[u'hiszpański'] = {u'Á': u'A',u'É': u'E',u'Í': u'I',u'Ó': u'O',u'Ú': u'U',u'á': u'a',u'é': u'e',u'í': u'i',u'ó': u'o',u'ú': u'u'}
    
    for lang in replace:
        cat = Category(site, u'Kategoria:%s (indeks)' % lang)
        lista_stron = pagegenerators.CategorizedPageGenerator(cat)
    
        for a in lista_stron:
            try: h = Haslo(a.title())
            except sectionsNotFound:
                pass
            except WrongHeader:
                pass
            else:
                if h.type == 3:    
                    for c in h.listLangs:
                        try: c.lang
                        except AttributeError:
                            pass
                        else:
                            if c.lang == lang:
                                first = c.title
                                temp = c.title
                                for rep in replace[lang]:
                                    temp = temp.replace(rep, replace[lang][rep])
                                if first != temp:
                                    c.headerArg = temp
                                    c.updateHeader()
                                    h.push(False, u'modyfikacja nagłówka w celu poprawnego indeksowania haseł (usunięcie znaków diakrytycznych)')
    
    
    #for p in lista_stron2:
    #    if any (item in p.text for item in lista):
    #        print u'*[[%s]]' % p.title
            
if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()