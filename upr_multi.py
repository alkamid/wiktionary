#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
#sys.path.append('/home/adam/wikt/pywikipedia')
sys.path.append('/home/alkamid/wikt/pywikipedia')
import pywikibot
from pywikibot import Category
from pywikibot import pagegenerators
import re
import codecs

def log_write(text):
    if test_mode == 1:
        print(text)
    else:
        if text != '':
            file = open("log/upr_multi.txt", 'a')
            file.write (text.encode("utf-8"))
            file.close

def main():
    global test_mode
    test_mode = 0
    global site
    site = pywikibot.Site()
    global site_en
    site_en = pywikibot.Site('en', 'wiktionary')

    inp = codecs.open('utftable.txt', encoding='utf-8')

    re_text_przed = re.compile('(.*{{kreski}}.*?\n).*?\n{{kolejność', re.DOTALL)
    re_text_po = re.compile('.*{{kreski}}.*?\n.*?(\n{{kolejność}}.*)', re.DOTALL)
    re_text = re.compile('{{kreski}}.*?\n(.*?)\n{{kolejność')
    re_text_w = re.compile('(.*?)( {{warianty-obrazek|)')
    re_text_obr = re.compile('.*?( {{warianty-obrazek.*)')
    re_trad = re.compile('{{zch-w\|ct\|(.)}}')
    re_upr = re.compile('{{zch-w\|cu\|(.)}}')
    re_uwagi_przed = re.compile('(.*{{słowniki.*?{{uwagi}})', re.DOTALL)
    re_uwagi_po = re.compile('{{słowniki.*?{{uwagi}}.*?({{źródła}}.*)', re.DOTALL)
    re_uwagi = re.compile('{{słowniki.*?{{uwagi}}(.*?){{źródła}}', re.DOTALL)
    uwagi = ' znak ten jest uproszczoną wersją kilku znaków tradycyjnych\n'

    inp_str = inp.read()
    inp = codecs.open('utftable.txt', encoding='utf-8')

    lista = []
    for line in inp:
        lista.append(line.split())
        print(line)

    dodane = []

    for line in lista:
        nowy = ''
        log = ''
        check = ''
        text_po = ''
        upr = line[0][0]
        re_all = re.compile('(%s=.)' % upr)
        s_all = re_all.findall(inp_str)
        if (len(s_all) > 1):

            if (upr not in dodane):
                nowy = '{{warianty'
                for b in s_all:
                    if b == s_all[0]:
                        check = '{{warianty | {{zch-w|ct|%s}} | {{zch-w|cu|%s}}}}' % (b[2],b[0])
                    nowy = nowy + ' | {{zch-w|ct|%s}}' % b[2]
                nowy = nowy + ' | {{zch-w|cu|%s}}}}' % upr

                page = pywikibot.Page(site, '%s' % upr)

                try:
                    exists = page.get()
                except pywikibot.NoPage:
                    log += '[[%s]] - nie istnieje na pl.wikt' % (upr)
                except pywikibot.IsRedirectPage:
                    log += '[[%s]] - przekierowanie na pl.wikt' % (upr)
                except pywikibot.Error:
                    print('nieznany błąd')
                else:
                    s_text_przed = re.search(re_text_przed, exists)
                    s_text = re.search(re_text, exists)
                    s_text_obr = re.search(re_text_obr, s_text.group(1))

                    text_w = ''
                    s_text_w = None
                    if s_text_obr == None:
                        text_w = s_text.group(1)
                    else:
                        s_text_w = re.search(re_text_w, s_text.group(1))
                        text_w = s_text_w.group(1)

                    s_text_po = re.search(re_text_po, exists)
                    if s_text_po == None:
                        log += '[[%s]] - problem ze znalezieniem sekcji' % (upr)

                    if text_w == check:
                        final = s_text_przed.group(1) + nowy
                        if s_text_obr:
                            final = final + s_text_obr.group(1)

                        s_uwagi = re.search(re_uwagi, s_text_po.group(1))
                        if s_uwagi:
                            if s_uwagi.group(1) == '\n':
                                s_uwagi_przed = re.search(re_uwagi_przed, s_text_po.group(1))
                                s_uwagi_po = re.search(re_uwagi_po, s_text_po.group(1))
                                if s_uwagi_przed and s_uwagi_po:
                                    text_po = s_uwagi_przed.group(1) + uwagi + s_uwagi_po.group(1)
                            else:
                                log += '[[%s]] - niepuste uwagi' % (upr)
                        final = final + text_po
                        if test_mode == 0:
                            page.put(final, comment='bot dodaje wersje tradycyjne znaku, źródło: http://simplify.codeplex.com/')
                        else:
                            print(final)
                    else:
                        log += '[[%s]] - check się nie zgadza' % (upr)


                dodane.append(upr)
                log_write(log)

if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
