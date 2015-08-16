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
    
    re_italics = re.compile(r'(?<!\')\'\'(?!\')(.*?)(?<!\')\'\'(?!\')')
    #replace = {}
    range1 = 1536
    range2 = 1791
    punct1 = 32
    punct2 = 64
    others = ('[', ']', '|')
    
    replace = ['arabski']
    
    for lang in replace:
        cat = Category(site, 'Kategoria:%s (indeks)' % lang)
        lista_stron = pagegenerators.CategorizedPageGenerator(cat, start='تونسي')
    
        #lista_stron = [pywikibot.Page(site, u'آيسلندا')]
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
                                italics = re.findall(re_italics, c.content)
                                if italics:
                                    for elem in italics:
                                        found = 0
                                        for lit in elem:
                                            num = ord(lit)
                                            #if not((num >= range1 and num <= range2) or (num >= punct1 and num <= punct2) or lit in others):
                                            if num >= range1 and num <= range2:
                                                found += 1
                                        if found:
                                            c.content = c.content.replace('\'\'%s\'\'' % elem, elem)
                    h.push(False, 'usunięcie kursywy w arabskim')
                                                
    
    
    #for p in lista_stron2:
    #    if any (item in p.text for item in lista):
    #        print u'*[[%s]]' % p.title
            
if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()