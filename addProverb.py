#!/usr/bin/python
# -*- coding: utf-8 -*-

import wikipedia
from klasa import *
import datetime
import time
    
def main():
    site = wikipedia.getSite()
    
    jakie = u'bengalskie'
    catname = u'Język bengalski'
    linkLang = u'bengalski'
    jakieCapital = jakie[0].upper() + jakie[1:]
    switch = 0
    #0 - Kategoria:Jakie przysłowia
    #1 - Kategoria:Przysłowia w jakie
    
    textTemplate = u'przysłowie %s<includeonly>[[Kategoria:' % jakie
    if not switch:
        newCat = u'%s przysłowia' % jakieCapital
    else:
        newCat = u'Przysłowia w %s' % jakie
    textTemplate += newCat
    textTemplate += u']]</includeonly><noinclude>[[Kategoria:Szablony przysłów|%s]]</noinclude>' % jakie
    
    textCategory = u'[[Kategoria:%s| ]]\n[[Kategoria:Przysłowia]]\n{{język linków|%s}}' % (catname, linkLang)
 
    pageTemplate = wikipedia.Page(site, u'Szablon:przysłowie %s' % jakie)
    try: pageTemplate.get()
    except wikipedia.NoPage:
        pageTemplate.put(textTemplate, comment=u"Dodanie szablonu dla przysłowia")
    else:
        print u'Szablon dla języka "%s" już istnieje!' % jakie
        
    pageCategory = wikipedia.Page(site, u'Kategoria:%s' % newCat)
    try: pageCategory.get()
    except wikipedia.NoPage:
        pageCategory.put(textCategory, comment=u"Dodanie kategorii dla przysłów")
    else:
        print u'Kategoria dla języka "%s" już istnieje!' % jakie
        
        
    langCategory = wikipedia.Page(site, u'Kategoria:%s' % catname)
    try: temp = langCategory.get()
    except wikipedia.NoPage:
        print u'Error: no such category: %s' % catname
    else:
        if u'\n|przysłowia=\n|' in temp:
            temp = temp.replace(u'\n|przysłowia=\n|', u'\n|przysłowia=%s\n|' % newCat)
            langCategory.put(temp, u'dodanie kategorii przysłów')
        else:
            print u'błąd - na stronie Kategoria:%s nie znaleziono parametru "przysłowia"' % catname
            
    
if __name__ == '__main__':
    try:
        main()
    finally:
        wikipedia.stopme()

