#!/usr/bin/python
# -*- coding: utf-8 -*-

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
            file = open("log/upr.txt", 'a')
            file.write (text.encode("utf-8"))
            file.close

def main():
    global test_mode
    test_mode = 0
    global site
    site = pywikibot.getSite()
    global site_en
    site_en = pywikibot.getSite('en', 'wiktionary')



    inp = codecs.open('utftable.txt', encoding='utf-8')

    re_text_przed = re.compile('(.*{{kreski}}.*?\n).*?\n{{kolejność', re.DOTALL)
    re_text_po = re.compile('.*{{kreski}}.*?\n.*?(\n{{kolejność}}.*)', re.DOTALL)
    re_text = re.compile('{{kreski}}.*?\n(.*?)\n{{kolejność')
    re_text_w = re.compile('(.*?)( {{warianty-obrazek|)')
    re_text_obr = re.compile('.*?( {{warianty-obrazek.*)')
    re_trad = re.compile('{{zch-w\|ct\|(.)}}')
    re_upr = re.compile('{{zch-w\|cu\|(.)}}')


    lista = []
    for line in inp:
        lista.append(line.split())

    for line in lista:
        upr = line[0][0]
        trad = line[0][2]

        log = ''
        nowy = ''

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

            if text_w == '{{warianty|{{zch-w}}}}':
                nowy = '{{warianty | {{zch-w|ct|%s}} | {{zch-w|cu|%s}}}}' % (trad, upr)
                final = s_text_przed.group(1) + nowy
                if s_text_obr:
                    final = final + s_text_obr.group(1)
                final = final + s_text_po.group(1)
                if test_mode == 0:
                    page.put(final, comment='bot dodaje znak tradycyjny/uproszczony, źródło: http://simplify.codeplex.com/')
                else:
                    print(final)
            else:
                s_trad = re.search(re_trad, s_text.group(1))
                s_upr = re.search(re_upr, s_text.group(1))
                if s_trad and s_trad.group(1) != trad:
                    log += '[[%s]] - zły znak tradycyjny' % (upr)
                if s_upr and s_upr.group(1) != upr:
                    log += '[[%s]] - zły znak uproszczony' % (upr)


        log_write(log)




if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
