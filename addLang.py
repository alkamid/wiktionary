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

def addLang(shortName, code, etym, shortOnly = False, jakie = None, zjezyka = None, sysop = False):
    """
    Add a new language to the technical pages.
    params:
        shortName (str): short language name, i.e. without "język"
        shortOnly (bool): some languages are referred to by their name only, e.g. "esperanto" (not "esperanto language") - in that case, set shortOnly to 1
        code (str): wikimedia or ISO code
        etym (str): abbreviation to use in {{etym}} template, chosen arbitrarily
        jakie (str): adjective: polski -> polskie, esperanto -> esperanckie, volapuk -> volapuk (only define for non-standard names, e.g. "norweski (bokmal)"
        zjezyka (str): "z języka polskiego", "z esperanto", "z języka akan" (only define for non-standard names, e.g. "norweski (bokmal)"
        sysop (bool): one page (MediaWiki:Gadget-langdata.js) requires sysop access. Because of how OAuth works, the script needs to be executed separately for this page
    """

    # Usually the input for this function is copied from user-created content
    # on Wiki. To make sure there are no invisible unwanted characters,
    # clean the input first
    clean_word_pattern = re.compile(r'\W+', re.UNICODE)
    shortName = clean_word_pattern.sub('', shortName)
    code = clean_word_pattern.sub('', code)
    etym = clean_word_pattern.sub('', etym)
    jakie = clean_word_pattern.sub('', jakie)
    zjezyka = clean_word_pattern.sub('', zjezyka)

    if jakie == None and zjezyka == None:
        if shortName.endswith('ski'):
            jakie = shortName + 'e'
            zjezyka = shortName + 'ego'
        else:
            jakie = shortName
            zjezyka = shortName
        
    site = pywikibot.Site()

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
        page1.text = '{{kategoria języka\n|nazwa polska=%s\n|nazwa własna=\n|język krótko=%s\n|z języka=%s\n|przysłowia=\n|podręcznik=\n|tworzenie haseł=\n|nagrania wymowy=\n|dodatkowe=\n}}\n\n[[Kategoria:Języki|%s]]' % (longNameCapital, shortName, zjezyka, shortName)
        page1.save(summary="Dodanie języka %s" % zjezyka)
        #print textPage1
    else:
        pywikibot.output('Kategoria języka "%s" już istnieje!' % shortName)

    #2. kategoria indeks
    page2 = pywikibot.Page(site, 'Kategoria:%s (indeks)' % shortName)
    try: page2.get()
    except pywikibot.NoPage:
        page2.text = '<div align=center>\'\'\'[[:Kategoria:%s|%s]]\'\'\'<p>{{indeks|%s}}</div>\n{{dodajhasło}}\n[[Kategoria:Indeks słów wg języków]]\n[[Kategoria:%s| ]]' % (longNameCapital, longNameCapital, shortName, longNameCapital)
        page2.save(summary="Dodanie języka %s" % zjezyka)
        #print textPage2
    else:
        pywikibot.output('Kategoria z indeksem języka "%s" już istnieje!' % shortName)

    #3. szablon języka
    page3 = pywikibot.Page(site, 'Szablon:%s' % longName)
    try: page3.get()
    except pywikibot.NoPage:
        page3.text = '<includeonly>{{nagłówek języka\n| długa          = %s\n| krótka         = %s\n| kod            = %s\n| klucz_indeksu       = {{{1|{{PAGENAME}}}}}\n}}</includeonly><noinclude>[[Kategoria:Szablony indeksujące języków| {{PAGENAME}}]]</noinclude>' % (longName, shortName, code)
        page3.save(summary="Dodanie języka %s" % zjezyka)
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
            page5.text = s_before.group(1)
            page5.text += ' |%s={{indeks/nowy|%s}}\n' % (shortName, shortName)
            page5.text += s_after.group(1)
            page5.save(summary="Dodanie języka %s" % zjezyka)
        else:
            pywikibot.output('Nie dodano parametru do szablonu {{indeks}}!')
    else:
        pywikibot.output('Nazwa języka (%s) istnieje już  w szablonie {{indeks}}' % shortName)
    
    #6. {{dopracować}}
    page6 = pywikibot.Page(site, 'Szablon:dopracować')
    if ' %s=' % shortName not in page6.get():
        hook = ' |#default=<br>Należy w nim poprawić: <i>{{{1}}}</i>[[Kategoria:Hasła do dopracowania|{{BASEPAGENAME}}]]'
        re_before = re.compile(r'(.*?)%s' % re.escape(hook), re.DOTALL)
        re_after = re.compile(r'.*?(%s.*)' % re.escape(hook), re.DOTALL)
        s_before = re.search(re_before, page6.get())
        s_after = re.search(re_after, page6.get())
        if s_before and s_after:
            page6.text = s_before.group(1)
            page6.text += ' | %s=[[Kategoria:Hasła %s do dopracowania|{{BASEPAGENAME}}]]\n' % (shortName, jakie)
            page6.text += s_after.group(1)
            page6.save(summary="Dodanie języka %s" % zjezyka)
        else:
            pywikibot.output('Nie dodano parametru do szablonu {{dopracować}}!')
    else:
        pywikibot.output('Nazwa języka (%s) istnieje już w szablonie {{dopracować}}' % shortName)
    
    #7. skróty do sekcji
    page7 = pywikibot.Page(site, 'Wikisłownik:Kody języków')
    if '{0}\n'.format(shortName) not in page7.get():
        hook = '|}\n\n== Linki zewnętrzne'
        re_before = re.compile(r'(.*?)%s' % re.escape(hook), re.DOTALL)
        re_after = re.compile(r'.*?(%s.*)' % re.escape(hook), re.DOTALL)
        s_before = re.search(re_before, page7.get())
        s_after = re.search(re_after, page7.get())
        if s_before and s_after:
            page7.text = s_before.group(1)
            page7.text += '|-\n|%s\n|%s\n' % (longName, code)
            page7.text += s_after.group(1)
            page7.save(summary="Dodanie języka %s" % zjezyka)
        else:
            pywikibot.output('\n----------------------------------------\nNie dodano parametru do strony Wikisłownik:Kody języków!\n--------------------\n')
    else:
        pywikibot.output('Nazwa języka (%s) istnieje już na stronie Wikisłownik:Kody języków' % shortName)

    #7a. etymologia - kategoria
    page71 = pywikibot.Page(site, 'Kategoria:%s w etymologii' % longNameCapital)
    try: page71.get()
    except pywikibot.NoPage:
        page71.text = '__HIDDENCAT__\n[[Kategoria:%s| ]]\n[[Kategoria:Relacje etymologiczne|%s]]' % (longNameCapital, shortName)
        page71.save(summary="Dodanie języka %s" % zjezyka)
    else:
        pywikibot.output('Kategoria etymologiczna języka "%s" już istnieje!' % shortName)

    #7b. etymologia Szablon:etym/język

    page72 = pywikibot.Page(site, 'Szablon:etym/język')
    if ('{0}\n'.format(shortName) not in page72.get()) and ('{0}\n'.format(shortName.title()) not in page72.get()):
        if ' %s=' % (etym) not in page72.get():
            hook = ' |inny\n}}<noinclude>'
            re_before = re.compile(r'(.*?)%s' % re.escape(hook), re.DOTALL)
            re_after = re.compile(r'.*?(%s.*)' % re.escape(hook), re.DOTALL)
            s_before = re.search(re_before, page72.get())
            s_after = re.search(re_after, page72.get())
            if s_before and s_after:
                page72.text = s_before.group(1)
                page72.text += ' |%s=%s\n' % (etym, longNameCapital)
                page72.text += s_after.group(1)
                page72.save(summary="Dodanie języka %s" % zjezyka)
            else:
                pywikibot.output('Nie dodano parametru do szablonu {{etym/język}}!')
        else:
            pywikibot.output('Taki skrót już istnieje w {{etym/język}}, wybierz inny')
    else:
        pywikibot.output('Nazwa języka (%s) istnieje już w szablonie {{etym/język}}' % shortName)
        

    #8. Moduł:statystyka/dane
    page8 = pywikibot.Page(site, 'Moduł:statystyka/dane')
    if '%s' % shortName not in page8.get():
        page8.text = page8.get()[:-40] + page8.get()[-40:].replace("\tdate =", "\t{ '%s' },\n\tdate =" % shortName)
        page8.save(summary="Dodanie języka %s" % zjezyka)
    else:
        pywikibot.output('Nazwa języka (%s) istnieje już na stronie Moduł:statystyka/dane' % shortName)


    if sysop:
        #9. MediaWiki:Gadget-langdata.js
        page10 = pywikibot.Page(site, 'MediaWiki:Gadget-langdata.js')
        if '"%s"' % (shortName) not in page10.text:
            changed = False
            hook = '\n\t},\n\tshortLangs:'
            re_before = re.compile(r'(.*?)%s' % re.escape(hook), re.DOTALL)
            re_after = re.compile(r'.*?(%s.*)' % re.escape(hook), re.DOTALL)
            s_before = re.search(re_before, page10.text)
            s_after = re.search(re_after, page10.text)
            if s_before and s_after:
                page10.text = s_before.group(1)
                page10.text += ',\n\t\t"%s"\t :"%s"' % (shortName, code)
                page10.text += s_after.group(1)
                changed = True
            else:
                pywikibot.output('Nie uzupełniono obiektu "lang2code" w MediaWiki:Gadget-langdata.js!')
            if shortOnly:
                re_short = re.compile(r'shortLangs: \[\n[^\]]+((?=\n\t\]))')
                s_short = re.search(re_short, page10.text)
                if s_short:
                    temp = page10.text
                    page10.text = temp[:s_short.start(1)]
                    page10.text += ',\n\t\t"%s"' % shortName
                    page10.text += temp[s_short.end(1):]
                    changed = True
                else:
                    pywikibot.output('Nie uzupełniono tablicy "shortLangs" w MediaWiki:Gadget-langdata.js!')
            if changed:
                page10.save(summary='Dodanie języka {0}'.format(zjezyka), as_group='sysop')
            else:
                pywikibot.output('Nie dodano parametru do strony MediaWiki:Gadget-langdata.js!')
        else:
            pywikibot.output('Nazwa języka (%s) istnieje już na stronie MediaWiki:Gadget-langdata.js' % shortName)


newlangs = [('tshangla', 'tsj', 'tsha')]
for lang in newlangs:
    addLang(*lang, shortOnly=False, sysop=False)
