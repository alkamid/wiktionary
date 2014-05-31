#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import Category
from pywikibot import pagegenerators
import re
from klasa import *
from main import *

def addOdczas(title):
    re_tabelkaAttr = re.compile(ur'\|\s*?(z|)robienie\s*?=(.*?)(?=}}|\n)')
    word = Haslo(title)

    log = u''
    if word.type == 3 and word.listLangs:
        for sekcja in word.listLangs:
            if sekcja.lang == u'polski':
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
                                log += u'*[[%s]] - redirect' % (odczasownikowy)
                            elif nowe.type == 1 and u' ' not in odczasownikowy:
                                nowaSekcja = Sekcja(title=odczasownikowy, type=9, lang=u'język polski')
                                nowaSekcja.znaczeniaDetail.append([u'\'\'rzeczownik, rodzaj nijaki\'\'', u'\n: (1.1) {{rzecz}} {{odczas}} \'\'od\'\' [[%s]]' % czasownik])
                                if odczasownikowy[-4:] == u'enie' or odczasownikowy[-4:] == u'anie' or odczasownikowy[-3:] == u'cie':
                                    pre = odczasownikowy[:-2]
                                    nowaSekcja.odmiana.text = u'\n: (1.1) {{odmiana-rzeczownik-polski\n|Mianownik lp = %sie\n|Dopełniacz lp = %sia\n|Celownik lp = %siu\n|Biernik lp = %sie\n|Narzędnik lp = %siem\n|Miejscownik lp = %siu\n|Wołacz lp = %sie\n}}' % (pre, pre, pre, pre, pre, pre, pre)
                                else:
                                    enieaniestop = 1
                                if not enieaniestop:
                                    nowaSekcja.antonimy.text = u'\n: (1.1) [[nie%s]]' % odczasownikowy
                                    nowaSekcja.saveChanges()
                                    page = pywikibot.Page(site, odczasownikowy)
                                    try: page.get()
                                    except pywikibot.NoPage:
                                        page.put(nowaSekcja.content, comment=u'dodanie hasła o rzeczowniku odczasownikowym na podstawie [[%s]]' % czasownik)
                            nieodczasownikowy = u'nie' + odczasownikowy
                            nowe = Haslo(nieodczasownikowy)
                            if nowe.type == 0:
                                log += u'*[[%s]] - redirect' % (nieodczasownikowy)
                            elif nowe.type == 1 and u' ' not in nieodczasownikowy:
                                nowaSekcja = Sekcja(title=nieodczasownikowy, type=9, lang=u'język polski')
                                nowaSekcja.znaczeniaDetail.append([u'\'\'rzeczownik, rodzaj nijaki\'\'', u'\n: (1.1) {{rzecz}} {{odczas}} \'\'od\'\' [[nie]] [[%s]]' % czasownik])
                                if not enieaniestop:
                                    pre = nieodczasownikowy[:-3]
                                    nowaSekcja.odmiana.text = u'\n: (1.1) {{odmiana-rzeczownik-polski\n|Mianownik lp = %snie\n|Dopełniacz lp = %snia\n|Celownik lp = %sniu\n|Biernik lp = %snie\n|Narzędnik lp = %sniem\n|Miejscownik lp = %sniu\n|Wołacz lp = %snie\n}}' % (pre, pre, pre, pre, pre, pre, pre)
                                    nowaSekcja.antonimy.text = u'\n: (1.1) [[%s]]' % odczasownikowy
                                    nowaSekcja.saveChanges()
                                    page = pywikibot.Page(site, nieodczasownikowy)
                                    try: page.get()
                                    except pywikibot.NoPage:
                                        page.put(nowaSekcja.content, comment=u'dodanie hasła o rzeczowniku odczasownikowym na podstawie [[%s]]' % czasownik)
     
def main():
    global odmOlafa
    odmOlafa = OdmianaOlafa()
    global site
    site = pywikibot.getSite()
    templatePage = pywikibot.Page(site, u'Szablon:ndk')
    #lista = pagegenerators.ReferringPageGenerator(templatePage, True, True, True)
    lista = [u'poszukać']
    for a in lista:
        addOdczas(a)
                        
if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()               