#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append('/home/adam/wikt/pywikipedia')
#sys.path.append('/home/alkamid/wikt/pywikipedia')
import pywikibot
from pywikibot import Category
from pywikibot import pagegenerators
import re
import codecs
from klasa import *

def main():


    lista = ReadList('/home/adam/wikt/moje/inne/bez_rodzaju.txt')
    #site = pywikibot.getSite('fr', 'wiktionary')
    #cat = Category(site,u'Catégorie:Noms_communs_en_français')
    #cat = Category(site,u'Catégorie:français')
    #lista = pagegenerators.CategorizedPageGenerator(cat)

    for a in lista:
        h = HasloFr(a[0])
        if h.type == 3:
            h.langs()
            for c in h.list_lang:
                if c.state == 1 and 'fr' in c.lang:
                    print('\n' + h.title)
                    c.pola()
                    if c.noun.typ:
                        if c.genre == 'm' or c.genre == 'f':
                            pl = Haslo(h.title)
                            if pl.type == 3:
                                pl.langs()
                                for d in pl.list_lang:
                                    if 'polski' in d.lang:
                                        d.pola()
                                        print(d.czescMowy)



if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
