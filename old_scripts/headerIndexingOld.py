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
    site = pywikibot.Site()

    replace = {}
    replace['nowogrecki'] = {'Ά': 'Α', 'Έ': 'Ε', 'Ί': 'Ι', 'Ϊ': 'Ι', 'Ό': 'Ο', 'Ύ': 'Υ', 'Ϋ': 'Υ', 'Ώ': 'Ω', 'ά': 'α', 'έ': 'ε', 'ί': 'ι', 'ϊ': 'ι', 'ΐ': 'ι', 'ό': 'ο', 'ύ': 'υ', 'ϋ': 'υ', 'ΰ': 'υ', 'ώ': 'ω', 'ς': 'σ'}
    replace['francuski'] = {'À': 'A', 'Â': 'A', 'Ç': 'C', 'É': 'E', 'È': 'E', 'Ë': 'E', 'Ê': 'E', 'Î': 'I', 'Ï': 'I', 'Ô': 'O', 'Œ': 'OE', 'Ù': 'U', 'Ú': 'U', 'Û': 'U', 'à': 'a', 'â': 'a', 'ç': 'c', 'é': 'e', 'è': 'e', 'ë': 'e', 'ê': 'e', 'î': 'i', 'ï': 'i', 'ô': 'o', 'œ': 'oe', 'ù': 'u', 'ú': 'u', 'û': 'u'}
    replace['hiszpański'] = {'Á': 'A','É': 'E','Í': 'I','Ó': 'O','Ú': 'U','á': 'a','é': 'e','í': 'i','ó': 'o','ú': 'u'}

    for lang in replace:
        cat = Category(site, 'Kategoria:%s (indeks)' % lang)
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
                                    h.push(False, 'modyfikacja nagłówka w celu poprawnego indeksowania haseł (usunięcie znaków diakrytycznych)')


    #for p in lista_stron2:
    #    if any (item in p.text for item in lista):
    #        print u'*[[%s]]' % p.title

if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
