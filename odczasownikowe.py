#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import Category
from pywikibot import pagegenerators
import re
from klasa import *
from main import *

def addOdczas(title):
    re_tabelkaAttr = re.compile(r'\|\s*?(z|)robienie\s*?=(.*?)(?=}}|\n)')
    word = Haslo(title)

    log = ''
    if word.type == 3 and word.listLangs:
        for sekcja in word.listLangs:
            if sekcja.lang == 'polski':
                sekcja.pola()
                try: sekcja.odmiana
                except AttributeError:
                    pass
                else:
                    s_tabelkaAttr = re.search(re_tabelkaAttr, sekcja.odmiana.text)
                    if s_tabelkaAttr:
                        odczasownikowy = s_tabelkaAttr.group(2).strip()
                        if odczasownikowy:
                            enieaniestop = 0
                            czasownik = sekcja.title
                            nowe = Haslo(odczasownikowy)
                            if nowe.type == 0:
                                log += '*[[%s]] - redirect' % (odczasownikowy)
                            elif nowe.type == 1 and ' ' not in odczasownikowy:
                                nowaSekcja = LanguageSection(title=odczasownikowy, type=9, lang='język polski')
                                nowaSekcja.znaczeniaDetail.append(['\'\'rzeczownik, rodzaj nijaki\'\'', '\n: (1.1) {{rzecz}} {{odczas}} \'\'od\'\' [[%s]]' % czasownik])
                                if odczasownikowy[-4:] == 'enie' or odczasownikowy[-4:] == 'anie' or odczasownikowy[-3:] == 'cie':
                                    pre = odczasownikowy[:-2]
                                    nowaSekcja.odmiana.text = '\n: (1.1) {{odmiana-rzeczownik-polski\n|Mianownik lp = %sie\n|Dopełniacz lp = %sia\n|Celownik lp = %siu\n|Biernik lp = %sie\n|Narzędnik lp = %siem\n|Miejscownik lp = %siu\n|Wołacz lp = %sie\n}}' % (pre, pre, pre, pre, pre, pre, pre)
                                else:
                                    enieaniestop = 1
                                if not enieaniestop:
                                    nowaSekcja.antonimy.text = '\n: (1.1) [[nie%s]]' % odczasownikowy
                                    nowaSekcja.saveChanges()
                                    page = pywikibot.Page(site, odczasownikowy)
                                    try: page.get()
                                    except pywikibot.NoPage:
                                        page.put(nowaSekcja.content, comment='dodanie hasła o rzeczowniku odczasownikowym na podstawie [[%s]]' % czasownik)
                            nieodczasownikowy = 'nie' + odczasownikowy
                            nowe = Haslo(nieodczasownikowy)
                            if nowe.type == 0:
                                log += '*[[%s]] - redirect' % (nieodczasownikowy)
                            elif nowe.type == 1 and ' ' not in nieodczasownikowy:
                                nowaSekcja = LanguageSection(title=nieodczasownikowy, type=9, lang='język polski')
                                nowaSekcja.znaczeniaDetail.append(['\'\'rzeczownik, rodzaj nijaki\'\'', '\n: (1.1) {{rzecz}} {{odczas}} \'\'od\'\' [[nie]] [[%s]]' % czasownik])
                                if not enieaniestop:
                                    pre = nieodczasownikowy[:-3]
                                    nowaSekcja.odmiana.text = '\n: (1.1) {{odmiana-rzeczownik-polski\n|Mianownik lp = %snie\n|Dopełniacz lp = %snia\n|Celownik lp = %sniu\n|Biernik lp = %snie\n|Narzędnik lp = %sniem\n|Miejscownik lp = %sniu\n|Wołacz lp = %snie\n}}' % (pre, pre, pre, pre, pre, pre, pre)
                                    nowaSekcja.antonimy.text = '\n: (1.1) [[%s]]' % odczasownikowy
                                    nowaSekcja.saveChanges()
                                    page = pywikibot.Page(site, nieodczasownikowy)
                                    try: page.get()
                                    except pywikibot.NoPage:
                                        page.put(nowaSekcja.content, comment='dodanie hasła o rzeczowniku odczasownikowym na podstawie [[%s]]' % czasownik)

def main():
    global odmOlafa
    odmOlafa = OdmianaOlafa()
    global site
    site = pywikibot.Site()
    templatePage = pywikibot.Page(site, 'Szablon:ndk')
    #lista = pagegenerators.ReferringPageGenerator(templatePage, True, True, True)
    lista = ['poszukać']
    for a in lista:
        addOdczas(a)

if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
