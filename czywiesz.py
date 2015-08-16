#!/usr/bin/python
# -*- coding: utf-8 -*-

# robienie listy haseł polskich bez wymowy

import codecs
import pywikibot
from pywikibot import pagegenerators
import re
import math
import datetime
import logging

def main():

    logging.basicConfig()

    wiki = pywikibot.Site('pl', 'wikipedia')
    wikt = pywikibot.Site('pl', 'wiktionary')

    output = pywikibot.Page(wikt, 'Wikipedysta:AlkamidBot/SG_Wikipedia')

    data = [] # tablica z datami: dzisiejszą, jutrzejszą i pojutrzejszą

    data_dzis = datetime.datetime.now() + datetime.timedelta(hours=2)
    data.append(data_dzis.strftime("%Y-%m-%d"))
    data_tekst = data_dzis.strftime("Ostatnia aktualizacja listy: %Y-%m-%d, %H:%M:%S")
    data_jutro = datetime.datetime.now() + datetime.timedelta(days=1, hours=2)
    data.append(data_jutro.strftime("%Y-%m-%d"))
    data_pojutrze = datetime.datetime.now() + datetime.timedelta(days=2, hours=2)
    data.append(data_pojutrze.strftime("%Y-%m-%d"))

    re_czywiesz = re.compile('(\.\.\..*?)}}<noinclude>', re.DOTALL) #wyłuskanie wikitekstu, w którym są odnośniki do artykułów
    re_aktualnosci = re.compile('(\*.*?)<!-- po ostatnim', re.DOTALL)
    re_namedal = re.compile('</div>(.*?)}}<div style', re.DOTALL)
    re_dobry = re.compile('{{#timel\:N}}(.*?)<div style=', re.DOTALL)
    re_nazwiska = re.compile('(^[A-Z].*? [A-Z][^\s]*)') #szukanie nazw własnych w celu ich odfiltrowania; prymitywny sposób: łapie tylko nazwy dwuczłonowe, z których każda rozpoczyna się wielką literą
    re_link = re.compile('\[\[(.*?)(\||\]\])') #wyszukiwanie linków - omija wersję widoczną na stronie, pobiera tylko linka do hasła
    re_liczby = re.compile('^[0-9]*$') #odfiltrowanie haseł składających się tylko z cyfr
    re_daty = re.compile('^[0-9]* (stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia)$') #odfiltrowanie haseł w stylu "3 października" czy "11 listopada"

    # collect hyperlinks from the following pages: Czy wiesz, Aktualności, Artykuł na medal, Dobry artykuł
    lista_linki = []

    for i in data:
        try:
            czywiesz = pywikibot.Page(wiki, 'Wikiprojekt:Czy_wiesz/ekspozycje/%s' % i).get()
        except pywikibot.NoPage:
            print('Warning: page Wikiprojekt:Czy_wiesz/ekspozycje/%s doesn\'t exist' % i)
        else:
            s_czywiesz = re.search(re_czywiesz, czywiesz)
            if s_czywiesz:
                s_link = re.findall(re_link, s_czywiesz.group(1))
                for a in s_link:
                    lista_linki.append(a[0])


    try:
        aktualnosci = pywikibot.Page(wiki, 'Szablon:Aktualności').get()
    except pywikibot.NoPage:
        print('Warning: page Szablon:Aktualności does not exist')
    else:
        s_aktualnosci = re.search(re_aktualnosci, aktualnosci)
        if s_aktualnosci:
            s_link = re.findall(re_link, s_aktualnosci.group(1))
            for a in s_link:
                if '#' not in a[0]:
                    lista_linki.append(a[0])

    try:
        namedal = pywikibot.Page(wiki, 'Szablon:Artykuł na medal').get()
    except pywikibot.NoPage:
        print('Warning: page Szablon:Artykuł na nie ma medalu!')
    else:
        s_namedal = re.search(re_namedal, namedal)
        if s_namedal:
            s_link = re.findall(re_link, s_namedal.group(1))
            for a in s_link:
                if '#' not in a[0] and 'Plik:' not in a[0]:
                    lista_linki.append(a[0])

    try:
        dobry = pywikibot.Page(wiki, 'Szablon:Dobry artykuł').get()
    except pywikibot.NoPage:
        print('Warning: page Szablon:Dobry artykuł does not exist')
    else:
        s_dobry = re.search(re_dobry, dobry)
        if s_dobry:
            s_link = re.findall(re_link, s_dobry.group(1))
            for a in s_link:
                if '#' not in a[0] and 'Plik:' not in a[0]:
                    lista_linki.append(a[0])

    #finished collecting hyperlinks

    nazwiska = '\n\n== prawdopodobne nazwy własne =='
    szablon = 'Jest to lista haseł, które aktualnie (dziś i w najbliższych dniach) pojawiają się na stronie głównej Wikipedii i nie mają tam szablonu kierującego do Wikisłownika. Oznacza to, że albo hasła u nas nie ma, albo wystarczy wstawić szablon (zazwyczaj {{s|wikisłownik}}, ale trzeba zwracać uwagę na infoboksy, które mogą przyjmować parametr "wikisłownik" lub "słownik"). Jeśli tworzysz u nas hasło z tej listy, nie zapomnij dodać szablonu {{s|wikipedia}}. Sekcja "prawdopodobne nazwy własne" ma mniejszy priorytet, ale i tak warto ją przejrzeć. Listę można edytować, bot i tak codziennie rano tworzy nową. Wszelkie uwagi dotyczące listy i pomysły na ulepszenie jej mile widziane na mojej [[Dyskusja Wikipedysty:Alkamid|stronie dyskusji]]. %s\n\n== wstawić szablon na Wikipedii ==' % data_tekst
    potrzebne = '\n\n== potrzebne =='

    for c in lista_linki:
        czyjest = pywikibot.Page(wiki, c)
        try:
            tekst = czyjest.get()
        except pywikibot.NoPage:
            print('nie ma na wiki')
        except pywikibot.IsRedirectPage:
            print('przekierowanie na wiki')
        else:
            re_wikislownik = re.compile('(wikisłownik\s*=\s*%s|słownik\s*=\s*%s|{{[wW]ikisłownik)' % (c, c))

            s_liczby = re.search(re_liczby, c)
            s_daty = re.search(re_daty, c)
            if not s_liczby and not s_daty:
                c_lower = c[0].lower() + c[1:]
                s_wikislownik = re.search(re_wikislownik, tekst)
                if not s_wikislownik:
                    s_nazwiska = re.search(re_nazwiska, c)
                    if s_nazwiska:
                        nazwiska = nazwiska + '\n*[[%s]]' % c
                    else:
                        upcase = '\n* WP: [[w:%s]]\t WS: [[%s]]' % (c, c)
                        upcase_switch = 0
                        try:
                            czyjest_wikt = pywikibot.Page(wikt, c).get()
                        except pywikibot.NoPage:
                            upcase_switch = 0
                        except pywikibot.IsRedirectPage:
                            upcase_switch = 0
                        else:
                            upcase_switch = 1

                        lowcase = ''
                        lowcase_switch = 0
                        if c[0].isupper():
                            lowcase = ' (lub [[%s]])' % c_lower
                            try:
                                czyjest_wikt = pywikibot.Page(wikt, c_lower).get()
                            except pywikibot.NoPage:
                                lowcase_switch = 0
                            except pywikibot.IsRedirectPage:
                                lowcase_switch = 0
                            else:
                                lowcase_switch = 1

                        noParens = ''
                        noParens_switch = 0
                        noParens_link = re.sub(r'\(.*?\)', '', c)
                        noParens_link = noParens_link.strip()
                        if noParens_link != c:
                            noParens = ' (lub [[%s]])' % noParens_link
                            try:
                                czyjest_wikt = pywikibot.Page(wikt, noParens_link).get()
                            except pywikibot.NoPage:
                                noParens_switch = 0
                            except pywikibot.IsRedirectPage:
                                noParens_switch = 0
                            else:
                                noParens_switch = 1

                        noParens_link_lower = noParens_link[0].lower() + noParens_link[1:]
                        lowcase_noParens = ''
                        lowcase_noParens_switch = 0
                        if noParens_link[0].isupper():
                            lowcase_noParens = ' (lub [[%s]])' % noParens_link_lower
                            try:
                                czyjest_wikt = pywikibot.Page(wikt, noParens_link_lower).get()
                            except pywikibot.NoPage:
                                lowcase_noParens_switch = 0
                            except pywikibot.IsRedirectPage:
                                lowcase_noParens_switch = 0
                            else:
                                lowcase_noParens_switch = 1

                        if upcase_switch or lowcase_switch or noParens_switch or lowcase_noParens_switch:
                            szablon = szablon + upcase + lowcase + noParens + lowcase_noParens
                        else:
                            potrzebne = potrzebne + upcase + lowcase + noParens + lowcase_noParens



    final = szablon + potrzebne + nazwiska

    if (len(output.get()) != len(final)):
        output.put(final, comment = 'Aktualizacja listy haseł występujących na stronie głównej Wikipedii')


if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
