#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append('/home/adam/pywiki/pywikipedia')
from pywikibot import Category
from pywikibot import pagegenerators
import pywikibot
import re

def main():
    site = pywikibot.getSite()
    indeks = pywikibot.Page(site, 'Indeks:Francuski_-_Związki_frazeologiczne')
    cat = Category(site,'Kategoria:francuski_(indeks)')
    gen1 = pagegenerators.CategorizedPageGenerator(cat)
    ex = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/wykluczone')
    re_obj = re.compile(r"''związek frazeologiczny''\n:\s*\(1\.1\) (\[\[[^]]*\]\])(\n|<ref)")
    tekst_dodaj = " zobacz też [[Indeks:Francuski - Związki frazeologiczne]]"

    zw = []
    trad = []
    lista = []
    for page in gen1:
        if ('związek frazeologiczny' in page.get()) and (page.title() not in indeks.get()) and (page.title() not in ex.get()):
            tlum = re_obj.search(page.get())
            if tlum != None:
                print(page, ' dodatek')
                zw.append(page.title())
                trad.append(tlum.group(1))
                print(tlum.group(1))
                if '[[Indeks: Francuski - Związki frazeologiczne]]' not in page.get() and '[[Indeks:Francuski - Związki frazeologiczne]]' not in page.get() and '{{źródła}}' in page.get():
                    sekcja_przed = re.search(r"(.*?)\n{{źródła}}", page.get(), re.DOTALL)
                    sekcja_po = re.search(r"({{źródła}}.*)", page.get(), re.DOTALL)
                    dozmiany = sekcja_przed.group(1)
                    dozmiany += tekst_dodaj
                    final = dozmiany + '\n' + sekcja_po.group(1)
                    page.put(final, comment = 'bot dodaje linka do indeksu związków frazeologicznych')
            else:
                text = ex.get()
                text += '\n* [[' + page.title() + ']]'
                ex.put(text, comment = 'bot dodaje wyjątek')
                print("zła: ", page)


    orig = indeks.get()
    for a, b in zip(zw, trad):
        lit = a[0]
        litcap = lit.capitalize()
        sekcja = re.search(r"== %s ==\n(.*?)\{\{do góry\}\}" % (litcap), orig, re.DOTALL)
        sekcja_przed = re.search(r"(.*?== %s ==\n)" % litcap, orig, re.DOTALL)
        sekcja_po = re.search(r"== %s ==\n.*?({{do góry}}.*)" % litcap, orig, re.DOTALL)
        lista = sekcja.group(1).split('\n')
        str = "* [[" + a + "]] → " + b
        lista.append(str)
        bez = [x for x in lista if len(x)>1]
        bez.sort()
        bez1 = "\n".join(bez) + "\n\n"
        orig = sekcja_przed.group(1) + bez1 + sekcja_po.group(1)

    indeks.put(orig, comment = 'bot aktualizuje indeks', botflag=False)

if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
