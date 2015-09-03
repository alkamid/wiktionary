#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import codecs
import pywikibot
from pywikibot import Category
from pywikibot import pagegenerators
import re
from pywikibot import xmlreader
from klasa import *

def main():

    site = pywikibot.getSite()

    inp = codecs.open('input/czescimowy_input.txt', encoding='utf-8')

    re_spacje = re.compile(r'\'\'(.*?)\'\'$')

    zamiana = []
    zamiana.append(['\'\'rzeczownik własny, rodzaj męski\'\'', '\'\'rzeczownik, rodzaj męski, nazwa własna\'\''])
    zamiana.append(['\'\'rzeczownik własny, rodzaj żeński\'\'', '\'\'rzeczownik, rodzaj żeński, nazwa własna\'\''])
    zamiana.append(['\'\'rzeczownik własny, rodzaj nijaki\'\'', '\'\'rzeczownik, rodzaj nijaki, nazwa własna\'\''])
    zamiana.append(['\'\'rzeczownik, nazwa własna, rodzaj męski\'\'', '\'\'rzeczownik, rodzaj męski, nazwa własna\'\''])
    zamiana.append(['\'\'rzeczownik, nazwa własna, rodzaj żeński\'\'', '\'\'rzeczownik, rodzaj żeński, nazwa własna\'\''])
    zamiana.append(['\'\'rzeczownik, nazwa własna, rodzaj nijaki\'\'', '\'\'rzeczownik, rodzaj nijaki, nazwa własna\'\''])
    zamiana.append(['\'\'rzeczownik, nazwa własna, rodzaj wspólny\'\'', '\'\'rzeczownik, rodzaj wspólny, nazwa własna\'\''])
    zamiana.append(['\'\'związek wyrazów w funkcji rzeczownika w rodzaju nijakim, nazwa własna\'\'', '\'\'związek wyrazów w funkcji rzeczownika rodzaju nijakiego, nazwa własna\'\''])
    zamiana.append(['\'\'związek wyrazów w funkcji rzeczownika w rodzaju męskim, nazwa własna\'\'', '\'\'związek wyrazów w funkcji rzeczownika rodzaju męskiego, nazwa własna\'\''])
    zamiana.append(['\'\'związek wyrazów w funkcji rzeczownika w rodzaju żeńskim, nazwa własna\'\'', '\'\'związek wyrazów w funkcji rzeczownika rodzaju żeńskiego, nazwa własna\'\''])
    zamiana.append(['\'\'zaimek pytający\'\'', '\'\'zaimek pytajny\'\''])
    zamiana.append(['\'\'związek wyrazów w funkcji rzeczownika, rodzaj żeński\'\'', '\'\'związek wyrazów w funkcji rzeczownika rodzaju żeńskiego\'\''])
    zamiana.append(['\'\'związek wyrazów w funkcji rzeczownika, rodzaj męski\'\'', '\'\'związek wyrazów w funkcji rzeczownika rodzaju męskiego\'\''])
    zamiana.append(['\'\'związek wyrazów w funkcji rzeczownika, rodzaj nijaki\'\'', '\'\'związek wyrazów w funkcji rzeczownika rodzaju nijakiego\'\''])
    zamiana.append(['\'\'związek wyrazów w funkcji rzeczownika, rodzaj żeński, nazwa własna\'\'', '\'\'związek wyrazów w funkcji rzeczownika rodzaju żeńskiego, nazwa własna\'\''])
    zamiana.append(['\'\'związek wyrazów w funkcji rzeczownika, rodzaj męski, nazwa własna\'\'', '\'\'związek wyrazów w funkcji rzeczownika rodzaju męskiego, nazwa własna\'\''])
    zamiana.append(['\'\'związek wyrazów w funkcji rzeczownika, rodzaj nijaki, nazwa własna\'\'', '\'\'związek wyrazów w funkcji rzeczownika rodzaju nijakiego, nazwa własna\'\''])
    #zamiana.append([u'\'\'rzeczownik, rodzaj żeński i męski\'\'', u'\'\'rzeczownik, rodzaj męski lub żeński\'\''])
    #zamiana.append([u'\'\'rzeczownik, rodzaj męski i żeński\'\'', u'\'\'rzeczownik, rodzaj męski lub żeński\'\''])
    zamiana.append(['\'\'rzeczownik, rodzaj żeński lub męski\'\'', '\'\'rzeczownik, rodzaj męski lub żeński\'\''])

    for a in zamiana:
        print('|-\n|%s\n|%s' % (a[0], a[1]))

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
                            d[0] = '\'\'%s\'\'' % (s_spacje.group(1).strip())
                            c.saveChanges()
                        for zm in zamiana:
                            if d[0] == zm[0]:
                                d[0] = d[0].replace(zm[0], zm[1])
                                c.saveChanges()


            h.push(False, 'Porządkowanie nagłówków sekcji znaczenia')


if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
