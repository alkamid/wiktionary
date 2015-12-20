#!/usr/bin/python
# -*- coding: utf-8 -*-

'''This script adds necessary pages/templates for a new language - what takes a human a few minutes, it does automatically'''

import pywikibot
from pywikibot import pagegenerators
import re
import collections
from klasa import *
import datetime
import time

def main():
    site = pywikibot.Site()

    '''Start input - remember to change the variables below!'''

    shortName = 'nanajski' #short language name, i.e. without "język"
    shortOnly = 0 #some languages are referred to by their name only, e.g. "esperanto" (not "esperanto language") - in that case, set shortOnly to 1
    kod = 'gld' #wikimedia or ISO code
    jakie = 'nanajskie' #adjective: polski -> polskie, esperanto -> esperanckie, volapuk -> volapuk
    zjezyka = 'nanajskiego' #"z' #"z języka polskiego", "z esperanto", "z języka akan"
    etymSkr = 'nanaj' #abbreviation to use in {{etym}} template, chosen arbitrarily

    '''End input'''


    if shortOnly:
        longName = shortName
    else:
        longName = 'język %s' % shortName

    #some templates/pages use "Język xxx", others use "język xxx"
    longNameCapital = longName[0].upper() + longName[1:]

    #kolejne czynności z http://pl.wiktionary.org/wiki/Wikis%C5%82ownik:Struktura_j%C4%99zyka_w_Wikis%C5%82owniku
    
    #1. kategoria główna
    page1 = pywikibot.Page(site, 'Kategoria:%s' % longNameCapital)
    try: page1.get()
    except pywikibot.NoPage:
        textPage1 = '{{kategoria języka\n|nazwa polska=%s\n|nazwa własna=\n|język krótko=%s\n|z języka=%s\n|przysłowia=\n|podręcznik=\n|tworzenie haseł=\n|nagrania wymowy=\n|dodatkowe=\n}}\n\n[[Kategoria:Języki|%s]]' % (longNameCapital, shortName, zjezyka, shortName)
        page1.put(textPage1, comment="Dodanie języka %s" % zjezyka)
        #print textPage1
    else:
        pywikibot.output('Kategoria języka "%s" już istnieje!' % shortName)

    #2. kategoria indeks
    page2 = pywikibot.Page(site, 'Kategoria:%s (indeks)' % shortName)
    try: page2.get()
    except pywikibot.NoPage:
        textPage2 = '<div align=center>\'\'\'[[:Kategoria:%s|%s]]\'\'\'<p>{{indeks|%s}}</div>\n{{dodajhasło}}\n[[Kategoria:Indeks słów wg języków]]\n[[Kategoria:%s| ]]' % (longNameCapital, longNameCapital, shortName, longNameCapital)
        page2.put(textPage2, comment="Dodanie języka %s" % zjezyka)
        #print textPage2
    else:
        pywikibot.output('Kategoria z indeksem języka "%s" już istnieje!' % shortName)

    #3. szablon języka
    page3 = pywikibot.Page(site, 'Szablon:%s' % longName)
    try: page3.get()
    except pywikibot.NoPage:
        textPage3 = '<includeonly>{{nagłówek języka\n| długa          = %s\n| krótka         = %s\n| kod            = %s\n| klucz_indeksu       = {{{1|{{PAGENAME}}}}}\n}}</includeonly><noinclude>[[Kategoria:Szablony indeksujące języków| {{PAGENAME}}]]</noinclude>' % (longName, shortName, kod)
        page3.put(textPage3, comment="Dodanie języka %s" % zjezyka)
        #print textPage3
    else:
        pywikibot.output('Szablon języka "%s" już istnieje!' % shortName)


    #5. {{indeks}}
    page5 = pywikibot.Page(site, 'Szablon:indeks')
    if '|%s=' % shortName not in page5.get():
        zaczepienie = ' |#default=\'Brak parametru. [http://pl.wiktionary.org/w/index.php?title=Wikis%C5%82ownik:Zg%C5%82o%C5%9B_b%C5%82%C4%85d_w_ha%C5%9Ble&action=edit&section=new Zgłoś problem].\''
        re_before = re.compile(r'(.*?)%s' % re.escape(zaczepienie), re.DOTALL)
        re_after = re.compile(r'.*?(%s.*)' % re.escape(zaczepienie), re.DOTALL)
        s_before = re.search(re_before, page5.get())
        s_after = re.search(re_after, page5.get())
        if s_before and s_after:
            textPage5 = s_before.group(1)
            textPage5 += ' |%s={{indeks/nowy|%s}}\n' % (shortName, shortName)
            textPage5 += s_after.group(1)
            page5.put(textPage5, comment="Dodanie języka %s" % zjezyka)
            #print textPage5
        else:
            pywikibot.output('Nie dodano parametru do szablonu {{indeks}}!')
    else:
        pywikibot.output('Nazwa języka (%s) istnieje już  w szablonie {{indeks}}' % shortName)
    
    #6. {{dopracować}}
    page6 = pywikibot.Page(site, 'Szablon:dopracować')
    if ' %s=' % shortName not in page6.get():
        zaczepienie = ' |#default=<br>Należy w nim poprawić: <i>{{{1}}}</i>[[Kategoria:Hasła do dopracowania|{{BASEPAGENAME}}]]'
        #zaczepienie = ' |#default=Należy w nim poprawić: \'\'{{{1}}}\'\'[[Kategoria:Hasła do dopracowania|{{BASEPAGENAME}}]]'
        re_before = re.compile(r'(.*?)%s' % re.escape(zaczepienie), re.DOTALL)
        re_after = re.compile(r'.*?(%s.*)' % re.escape(zaczepienie), re.DOTALL)
        s_before = re.search(re_before, page6.get())
        s_after = re.search(re_after, page6.get())
        if s_before and s_after:
            textPage6 = s_before.group(1)
            textPage6 += ' | %s=[[Kategoria:Hasła %s do dopracowania|{{BASEPAGENAME}}]]\n' % (shortName, jakie)
            textPage6 += s_after.group(1)
            page6.put(textPage6, comment="Dodanie języka %s" % zjezyka)
            #print textPage6
        else:
            pywikibot.output('Nie dodano parametru do szablonu {{dopracować}}!')
    else:
        pywikibot.output('Nazwa języka (%s) istnieje już w szablonie {{dopracować}}' % shortName)
    
    #7. skróty do sekcji
    page7 = pywikibot.Page(site, 'Wikisłownik:Kody języków')
    if ' %s\n' % shortName not in page7.get():
        zaczepienie = '|}\n\n== Linki zewnętrzne'
        re_before = re.compile(r'(.*?)%s' % re.escape(zaczepienie), re.DOTALL)
        re_after = re.compile(r'.*?(%s.*)' % re.escape(zaczepienie), re.DOTALL)
        s_before = re.search(re_before, page7.get())
        s_after = re.search(re_after, page7.get())
        if s_before and s_after:
            textPage7 = s_before.group(1)
            textPage7 += '|-\n|%s\n|%s\n' % (longName, kod)
            textPage7 += s_after.group(1)
            page7.put(textPage7, comment="Dodanie języka %s" % zjezyka)
            #print textPage7
        else:
            pywikibot.output('\n----------------------------------------\nNie dodano parametru do strony Wikisłownik:Kody języków!\n--------------------\n')
    else:
        pywikibot.output('Nazwa języka (%s) istnieje już na stronie Wikisłownik:Kody języków' % shortName)

    #7a. etymologia - kategoria
    page71 = pywikibot.Page(site, 'Kategoria:%s w etymologii' % longNameCapital)
    try: page71.get()
    except pywikibot.NoPage:
        textPage71 = '__HIDDENCAT__\n[[Kategoria:%s| ]]\n[[Kategoria:Relacje etymologiczne|%s]]' % (longNameCapital, shortName)
        page71.put(textPage71, comment="Dodanie języka %s" % zjezyka)
        #print textPage1
    else:
        pywikibot.output('Kategoria etymologiczna języka "%s" już istnieje!' % shortName)

    #7b. etymologia Szablon:etym/język

    page72 = pywikibot.Page(site, 'Szablon:etym/język')
    if '%s\n' % shortName not in page72.get():
        if ' %s=' % (etymSkr) not in page72.get():
            zaczepienie = ' |inny\n}}<noinclude>'
            re_before = re.compile(r'(.*?)%s' % re.escape(zaczepienie), re.DOTALL)
            re_after = re.compile(r'.*?(%s.*)' % re.escape(zaczepienie), re.DOTALL)
            s_before = re.search(re_before, page72.get())
            s_after = re.search(re_after, page72.get())
            if s_before and s_after:
                textPage72 = s_before.group(1)
                textPage72 += ' |%s=%s\n' % (etymSkr, longNameCapital)
                textPage72 += s_after.group(1)
                page72.put(textPage72, comment="Dodanie języka %s" % zjezyka)
                #print textPage7
            else:
                pywikibot.output('Nie dodano parametru do szablonu {{etym/język}}!')
        else:
            pywikibot.output('Taki skrót już istnieje w {{etym/język}}, wybierz inny')
    else:
        pywikibot.output('Nazwa języka (%s) istnieje już w szablonie {{etym/język}}' % shortName)
        

    #9. MediaWiki:Gadget-langdata.js
    page10 = pywikibot.Page(site, 'MediaWiki:Gadget-langdata.js')
    if '"%s"' % (shortName) not in page10.text:
        zaczepienie = '\n\t},\n\tshortLangs:'
        re_before = re.compile(r'(.*?)%s' % re.escape(zaczepienie), re.DOTALL)
        re_after = re.compile(r'.*?(%s.*)' % re.escape(zaczepienie), re.DOTALL)
        s_before = re.search(re_before, page10.text)
        s_after = re.search(re_after, page10.text)
        if s_before and s_after:
            textPage10 = s_before.group(1)
            textPage10 += ',\n\t\t"%s"\t :"%s"' % (shortName, kod)
            textPage10 += s_after.group(1)
            page10.text = textPage10
            site.logout()
            site.login(sysop=True) # need to be sysop to edit this page
            page10.save(summary='Dodanie języka {0}'.format(zjezyka), as_group='sysop')
            #print textPage10
        else:
            pywikibot.output('Nie dodano parametru do strony MediaWiki:Gadget-langdata.js!')
    else:
        pywikibot.output('Nazwa języka (%s) istnieje już na stronie MediaWiki:Gadget-langdata.js' % shortName)
    

    #8. Moduł:statystyka/dane
    page8 = pywikibot.Page(site, 'Moduł:statystyka/dane')
    if '%s' % shortName not in page8.get():
        textPage8 = page8.get()[:-40] + page8.get()[-40:].replace("\tdate =", "\t{ '%s' },\n\tdate =" % shortName)
        page8.put(textPage8, comment="Dodanie języka %s" % zjezyka)
    else:
        pywikibot.output('Nazwa języka (%s) istnieje już na stronie Moduł:statystyka/dane' % shortName)


if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
