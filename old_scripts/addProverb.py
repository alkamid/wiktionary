#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot
from klasa import *
import datetime
import time

def main():
    site = pywikibot.Site()

    jakie = 'bengalskie'
    catname = 'Język bengalski'
    linkLang = 'bengalski'
    jakieCapital = jakie[0].upper() + jakie[1:]
    switch = 0
    #0 - Kategoria:Jakie przysłowia
    #1 - Kategoria:Przysłowia w jakie

    textTemplate = 'przysłowie %s<includeonly>[[Kategoria:' % jakie
    if not switch:
        newCat = '%s przysłowia' % jakieCapital
    else:
        newCat = 'Przysłowia w %s' % jakie
    textTemplate += newCat
    textTemplate += ']]</includeonly><noinclude>[[Kategoria:Szablony przysłów|%s]]</noinclude>' % jakie

    textCategory = '[[Kategoria:%s| ]]\n[[Kategoria:Przysłowia]]\n{{język linków|%s}}' % (catname, linkLang)

    pageTemplate = pywikibot.Page(site, 'Szablon:przysłowie %s' % jakie)
    try: pageTemplate.get()
    except pywikibot.NoPage:
        pageTemplate.put(textTemplate, comment="Dodanie szablonu dla przysłowia")
    else:
        print('Szablon dla języka "%s" już istnieje!' % jakie)

    pageCategory = pywikibot.Page(site, 'Kategoria:%s' % newCat)
    try: pageCategory.get()
    except pywikibot.NoPage:
        pageCategory.put(textCategory, comment="Dodanie kategorii dla przysłów")
    else:
        print('Kategoria dla języka "%s" już istnieje!' % jakie)


    langCategory = pywikibot.Page(site, 'Kategoria:%s' % catname)
    try: temp = langCategory.get()
    except pywikibot.NoPage:
        print('Error: no such category: %s' % catname)
    else:
        if '\n|przysłowia=\n|' in temp:
            temp = temp.replace('\n|przysłowia=\n|', '\n|przysłowia=%s\n|' % newCat)
            langCategory.put(temp, 'dodanie kategorii przysłów')
        else:
            print('błąd - na stronie Kategoria:%s nie znaleziono parametru "przysłowia"' % catname)


if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
