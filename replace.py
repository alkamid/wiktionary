#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import Category
from pywikibot import pagegenerators
import re
from klasa import *

def main():
    global site
    site = pywikibot.getSite()
    templatePage1 = pywikibot.Page(site, 'Szablon:forma czasownika')
    templatePage2 = pywikibot.Page(site, 'Szablon:forma rzeczownika')
    templatePage3 = pywikibot.Page(site, 'Szablon:forma przymiotnika')
    templatePage4 = pywikibot.Page(site, 'Szablon:forma przysłówka')
    templatePage5 = pywikibot.Page(site, 'Szablon:forma zaimka')
    templatePage6 = pywikibot.Page(site, 'Szablon:morfem')
    templatePage7 = pywikibot.Page(site, 'Szablon:szwedzki czasownik frazowy')
    lista1 = list(pagegenerators.ReferringPageGenerator(templatePage1, True, True, True))
    lista2 = list(pagegenerators.ReferringPageGenerator(templatePage2, True, True, True))
    lista3 = list(pagegenerators.ReferringPageGenerator(templatePage3, True, True, True))
    lista4 = list(pagegenerators.ReferringPageGenerator(templatePage4, True, True, True))
    lista5 = list(pagegenerators.ReferringPageGenerator(templatePage5, True, True, True))
    lista6 = list(pagegenerators.ReferringPageGenerator(templatePage6, True, True, True))
    lista7 = list(pagegenerators.ReferringPageGenerator(templatePage7, True, True, True))
    lista = set(lista6 + lista7)
    re_forma = re.compile('^{{forma (czasownika|przymiotnika|rzeczownika|przysłówka|zaimka)(|\|[a-z]{2})}}$')
    re_morfem = re.compile('^{{morfem(|\|(eo|esperanto))(|\|(przedrostek|przedrostkowy|przyrostek|przyrostkowy))}}$')
    
    for a in lista:
        try: word = Haslo(a.title())
        except sectionsNotFound:
            pass
        except WrongHeader:
            pass
        else:
            if word.type == 3:
                change = 0
                for lang in word.listLangs:
                    if lang.type != 2:
                        lang.pola()
                        if lang.type not in (2,3,4,5,7,11):
                            pos = lang.znaczeniaDetail
                            for each in pos:
                                s_forma = re.search(re_forma, each[0])
                                s_morfem = re.search(re_morfem, each[0])
                                if s_forma or s_morfem or each[0] == '{{szwedzki czasownik frazowy}}':
                                    each[0] = '\'\'%s\'\'' % (each[0])
                                    change = 1
                                    lang.saveChanges()
                if change:
                    word.push(False, myComment='ujednolicenie zapisu części mowy (dodanie apostrofów przy szablonach)')
            '''s01 = re.search(re01, text)  
            if s01:
                text = re01.sub(ur'{{odczasownikowy od|nie|\1}}', text)
            s02 = re.search(re02, text)
            if s02:
                text = re02.sub(ur'{{odczasownikowy od|nie|\1}}', text)
            s03 = re.search(re03, text)
            if s03:
                text = re03.sub(ur'{{odczasownikowy od|nie|\1}}', text)
            s1 = re.search(re1, text)
            if s1:
                text = re1.sub(ur'{{odczasownikowy od|\1}}', text)
            s2 = re.search(re2, text)
            if s2:
                text = re2.sub(ur'{{odczasownikowy od|\1}}', text)
            s3 = re.search(re3, text)
            if s3:
                text = re3.sub(ur'{{odczasownikowy od|\1}}', text)'''
            #text = text.replace(u'{{odczasownikowy od||', u'{{odczasownikowy od|')
            #if first != text:
                #a.put(text, comment=u'Wprowadzenie szablonu {{s|odczasownikowy od}}')
                        
if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()               