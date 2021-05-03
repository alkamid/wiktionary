#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append('/home/adam/wikt/pywikipedia')
#sys.path.append('/home/alkamid/wikt/pywikipedia')
import pywikibot
from pywikibot import Category
from pywikibot import pagegenerators
import re
from klasa import *

def main():

    site = pywikibot.Site()
    cat = Category(site,'Kategoria:francuski (indeks)')
    lista = pagegenerators.CategorizedPageGenerator(cat, start='tænia')

    for a in lista:
        h = Haslo(a.title())
        if h.typ == 3:
            h.sekcje()
            for c in h.lista_sekcje:
                if 'francuski' in c.jezyk:
                    print('\n' + h.tytul)
                    c.pola()
                    print(c.wymowa.tresc)

if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
