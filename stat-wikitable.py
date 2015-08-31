#!/usr/bin/python
# -*- coding: utf-8 -*-

# tworzy wikitabelę z outputu statystyki

import sys
sys.path.append('/home/adam/pywiki/pywikipedia')
import codecs
import pywikibot

def main():

    offline_mode = 0
    site = pywikibot.getSite()
    page_dlugosc = pywikibot.Page(site, 'Wikipedysta:Alkamid/statystyka/długość')
    page_srednia = pywikibot.Page(site, 'Wikipedysta:Alkamid/statystyka/długość_średnia')
    page_multimedia = pywikibot.Page(site, 'Wikipedysta:Alkamid/statystyka/multimedia')

    lista = []
    inp = codecs.open('outputstat11.txt', encoding='utf-8')

    for line in inp:
        if not line.isspace():
            lista.append(line.split())

    def sortkey(row):
        return float(row[3])

    lista.sort(key=sortkey, reverse=True)

    text1 = '{| border=0 cellspacing=0 cellpadding=0\n|\n{| class="wikitable" style="margin: 0px; text-align:right;"\n! miejsce'
    text2 = '\n|}\n|\n{| class="wikitable sortable" style="margin: 0 auto; white-space: nowrap"\n! język !! suma długości haseł (w tys.) !! liczba haseł\n'
    text3 = text1
    text4 = '\n|}\n|\n{| class="wikitable sortable" style="margin: 0 auto; white-space: nowrap"\n! język !! średnia długość hasła !! liczba haseł\n'
    text5 = text1
    text6 = '\n|}\n|\n{| class="wikitable sortable" style="margin: 0 auto; white-space: nowrap"\n! język !! % z grafiką !! z grafiką !! % z nagraniem !! z nagraniem !! liczba haseł\n'

    for a in lista:
        a[0] = a[0].replace('_', ' ', 1)

    i = 1
    for a in lista:
        text1 = text1 + '\n|-\n! %d' % (i)
        text2 = text2 + '|-\n| [[:Kategoria:%s (indeks)|%s]]\n| align="right"| %.0f\n| align="right"| %.0f\n' % (a[0], a[0], float(a[3]), float(a[2]))
        i += 1

    def sortkey(row):
        return float(row[1])

    lista.sort(key=sortkey, reverse=True)

    i = 1
    for a in lista:
        text3 = text3 + '\n|-\n! %d' % (i)
        text4 = text4 + '|-\n| [[:Kategoria:%s (indeks)|%s]]\n| align="right"| %.1f\n| align="right"| %.0f\n' % (a[0], a[0], float(a[1]), float(a[2]))
        i += 1

    def sortkey(row):
        return float(row[7])

    lista.sort(key=sortkey, reverse=True)

    i = 1
    for a in lista:
        text5 = text5 + '\n|-\n! %d' % (i)
        text6 = text6 + '|-\n| [[:Kategoria:%s (indeks)|%s]]\n| align="right"| %.1f\n| align="right"| %.0f\n| align="right"| %.1f\n| align="right"| %.0f\n| align="right"| %.0f\n' % (a[0], a[0], float(a[7]), float(a[6]), float(a[5]), float(a[4]), float(a[2]))
        i += 1

    text_dlugosc = text1 + text2 + '|}\n|}'
    text_srednia = text3 + text4 + '|}\n|}'
    text_multimedia = text5 + text6 + '|}\n|}'

    filename_dlugosc = "wikitable-dlugosc.txt"
    filename_srednia = "wikitable-srednia.txt"
    filename_multimedia = "wikitable-multimedia.txt"

    file = open(filename_dlugosc, 'w')
    file.write(text_dlugosc)
    file.close
    file = open(filename_srednia, 'w')
    file.write(text_srednia)
    file.close
    file = open(filename_multimedia, 'w')
    file.write(text_multimedia)
    file.close

    if (offline_mode == 0):
        page_dlugosc.put(text_dlugosc, comment="Aktualizacja statystyk, dane z 3.09.2010", botflag=False)
        page_srednia.put(text_srednia, comment="Aktualizacja statystyk, dane z 3.09.2010", botflag=False)
        page_multimedia.put(text_multimedia, comment="Aktualizacja statystyk, dane z 3.09.2010", botflag=False)


if __name__ == '__main__':
    main()
