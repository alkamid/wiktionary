#!/usr/bin/python
# -*- coding: utf-8 -*-

# fr-verbes v1.04

""" changelog:
1.04
- {{odmiana|francuski}} -> {{odmiana}}
- od tej wersji bot może dodawać znaczenia, pod warunkiem że ostatnią edycję wykonał on sam lub Interwicket (jeśli ten drugi, to dodatkowym warunkiem jest przedostatnia edycja AlkamidBota)
- test_mode - dla true tylko wyświetla zmiany na ekranie, dla false działa na Wikisłowniku
"""

import pywikibot
import re
import time

def main():
    test_mode = 0;
    site = pywikibot.Site()
    spis = pywikibot.Page(site, 'Wikipedysta:Alkamid/formy_czas_franc')
    #logi = pywikibot.Page(site, u'Wikipedysta:AlkamidBot/do_sprawdzenia')
    #prop = pywikibot.Page(site, u'Wikipedysta:AlkamidBot/propozycje')
    lista = []
    podlista = [s.split(' # ') for s in spis.get().split('\n')] #bot pobiera listę i dzieli każde słowo na 1. hasło, 2. definicję, 3. wymowę IPA
    regex_sekcja = re.compile(r'==.*?{{(?:język francuski)?}}') #do sprawdzenia czy istnieje jakaś sekcja poza francuskim
    regex_znaczenia = re.compile(r'(rzeczownik|czasownik\b|przymiotnik|przysłówek|przymiotnik|liczebnik|partykuła|zaimek|przyimek|spójnik|wykrzyknik|związek frazeologiczny|przysłowie)') #sprawdza czy słowo występuje jako inna część mowy - znikomy ułamek haseł, ale w przyszłości mogę dodać obsługę
    for b in podlista:
        page = pywikibot.Page(site, b[0])
        try:
            text = page.get()
        except pywikibot.NoPage:
            textNew = "== %s ({{język francuski}}) ==\n{{wymowa}} {{IPA3|%s}}\n{{znaczenia}}\n{{forma czasownika|fr}}\n: (1.1) %s\n{{odmiana}}\n{{przykłady}}\n: (1.1)\n{{składnia}}\n{{kolokacje}}\n{{synonimy}}\n{{antonimy}}\n{{pokrewne}}\n{{frazeologia}}\n{{etymologia}}\n{{uwagi}}\n{{źródła}}" % (b[0], b[2], b[1])
            if (test_mode):
                print(("---- NOWA ---- %s:\n%s" % (b[0], textNew)).encode('utf-8'))
            else:
                page.put(textNew, comment = "bot dodaje odmianę czasownika francuskiego")

        except pywikibot.IsRedirectPage:
            logi = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/do_sprawdzenia')
            logNew = logi.get()
            logNew += "<br />[[%s]] - twarde przekierowanie" % (b[0])
            if (test_mode):
                print(("---- LOG ---- %s nowy wyjątek - twarde przekierowanie" % (b[0])).encode('utf-8'))
            else:
                logi.put(logNew, comment = "nowy wyjątek - twarde przekierowanie")

        except pywikibot.Error:
            logi = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/do_sprawdzenia')
            logNew = logi.get()
            logNew += "<br />[[%s]] - nieznany błąd" % (b[0])
            if (test_mode):
                print(("---- LOG ---- %s nowy wyjątek - nieznany błąd" % (b[0])).encode('utf-8'))
            else:
                logi.put(logNew, comment = "nowy wyjątek - nieznany błąd")

        else:
            if b[1] in text:
                logi = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/do_sprawdzenia')
                logNew = logi.get()
                logNew += "<br />[[%s]] - znaczenie %s już istnieje" % (b[0], b[1])
                if (test_mode):
                    print(("---- LOG ---- %s - znaczenie %s już istnieje" % (b[0], b[1])).encode('utf-8'))
                else:
                    logi.put(logNew, comment = "nowy wyjątek - znaczenie już istnieje")
            else:
                szukajSekcji = regex_sekcja.search(text)
                if szukajSekcji != None: #jeśli jest tylko sekcja francuska, to...
                    szukajZnaczen = regex_znaczenia.search(text)
                    if szukajZnaczen != None: #jeśli są inne znaczenia niż 'forma czasownika', to...
                        logi = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/do_sprawdzenia')
                        logNew = logi.get()
                        logNew += "<br />[[%s]] - występują inne znaczenia" % (b[0])
                        if (test_mode):
                            print(("---- LOG ---- %s - nowy wyjątek - występują inne znaczenia" % (b[0])).encode('utf-8'))
                        else:
                            logi.put(logNew, comment = "nowy wyjątek - inne znaczenia")
                    else:
                        history = page.getVersionHistory()
                        if (history[0][2] == 'AlkamidBot' or (history[1][2] == 'AlkamidBot' and history[0][2] == 'Interwicket')):
                            for i in range(1,47): #różnych form jest 47
                                j = i-1
                                szukaj = '(1.%s)' % i
                                prev = '(1.%s)' % j
                                if szukaj in text: #przeskocz na koniec listy znaczeń
                                    continue
                                else:
                                    strona_przed = re.search(r'(.*\{\{forma czasownika\|fr\}\}.*?%s.*?\n)' % (re.escape(prev)), text, re.DOTALL)
                                    strona_po = re.search(r'.*\{\{forma czasownika\|fr\}\}.*?%s.*?\n(.*)' % (re.escape(prev)), text, re.DOTALL)
                                    dodajTekst = strona_przed.group(1) + ': ' + szukaj + ' ' + b[1] + '\n' + strona_po.group(1)
                                    if (test_mode):
                                        print('---- EDYCJA ---- %s:\n%s' % (page, dodajTekst))
                                    else:
                                        page.put(dodajTekst, comment = "bot dodaje znaczenie %s" % (szukaj))
                                    break
                        else:
                            logi = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/do_sprawdzenia')
                            logNew = logi.get()
                            logNew += "<br />[[%s]] - ostatnim edytorem nie był AlkamidBot/Interwicket" % (b[0])
                            if (test_mode):
                                print(("---- LOG ---- %s - ostatnim edytorem nie był AlkamidBot" % (b[0]).encode('utf-8')))
                            else:
                                logi.put(logNew, comment = "nowy wyjątek - ostatnim edytorem nie był AlkamidBot/Interwicket")

                            for i in range(1,47): #różnych form jest 47
                                j = i-1
                                szukaj = '(1.%s)' % i
                                prev = '(1.%s)' % j
                                if szukaj in text: #przeskocz na koniec listy znaczeń
                                    continue
                                else:
                                    strona_przed = re.search(r'(.*\{\{forma czasownika\|fr\}\}.*?%s.*?\n)' % (re.escape(prev)), text, re.DOTALL)
                                    strona_po = re.search(r'.*\{\{forma czasownika\|fr\}\}.*?%s.*?\n(.*)' % (re.escape(prev)), text, re.DOTALL)
                                    dodajTekst = strona_przed.group(1) + ': ' + szukaj + ' ' + b[1] + '\n' + strona_po.group(1)
                                    prop = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/propozycje')
                                    propozycja = prop.get() + '\n\n\n<br /><br /><h3>[[' + b[0] + ']]</h3>\n' + dodajTekst
                                    if (test_mode):
                                        print('---- EDYCJA ---- %s:\n%s' % (page, dodajTekst))
                                    else:
                                        prop.put(propozycja, comment = "bot umieszcza proponowany wygląd hasła [[%s]]" % (b[0]))
                                    break
                else:
                    logi = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/do_sprawdzenia')
                    logNew = logi.get()
                    logNew += '<br />[[%s]] - istnieje, ale bez j. francuskiego' % (page.title())
                    if (test_mode):
                        print('---- LOG ---- %s - nowy wyjątek - nie ma j. francuskiego' % (page))
                    else:
                        logi.put(logNew, comment = "nowy wyjątek - nie ma j. francuskiego")
                    text += "\n\n== %s ({{język francuski}}) ==\n{{wymowa}} {{IPA3|%s}}\n{{znaczenia}}\n{{forma czasownika|fr}}\n: (1.1) %s\n{{odmiana}}\n{{przykłady}}\n: (1.1)\n{{składnia}}\n{{kolokacje}}\n{{synonimy}}\n{{antonimy}}\n{{pokrewne}}\n{{frazeologia}}\n{{etymologia}}\n{{uwagi}}\n{{źródła}}" % (b[0], b[2], b[1])
                    prop = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/propozycje')
                    propozycja = prop.get() + text
                    if (test_mode):
                        print('---- EDYCJA ---- %s:\n%s' % (page, text))
                    else:
                        prop.put(propozycja, comment = "bot umieszcza proponowany wygląd hasła [[%s]]" % (b[0]))


if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
