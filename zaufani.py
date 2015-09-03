#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators
import re
from pywikibot import xmlreader
import collections
from klasa import *
import datetime
import time

def main():
    site = pywikibot.getSite()

    username = 'Richiski'
    outputPage = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/zaufani/%s' % username)

    botNames = ['Tsca.bot', 'EquadusBot', 'Olafbot', 'MastiBot', 'AlkamidBot', 'Interwicket', 'RobotGMwikt']

    verified = []
    output = 'Lista haseł, które edytował tylko Richiski i następujące boty: Tsca.bot, EquadusBot, Olafbot, MastiBot, AlkamidBot, Interwicket, RobotGMwikt. Każde z poniższych, które ma status wersji nieprzejrzanej, można (i należy) przejrzeć bez sprawdzania, ponieważ jest to pozostałość sprzed wprowadzenia wersji przejrzanych i statusu redaktora.\n\n'

    cat = Category(site,'Kategoria:hiszpański (indeks)')
    cat2 = Category(site, 'Kategoria:nowogrecki (indeks)')
    lista_stron = pagegenerators.CategorizedPageGenerator(cat)
    lista_stron2 = pagegenerators.CategorizedPageGenerator(cat2)

    nadanieUprawnien = datetime.date(2009, 12, 12)

    time_format = "%Y-%m-%dT%H:%M:%SZ"

    for a in lista_stron:
        revs = a.getVersionHistory(reverseOrder=True)
        check = 0
        first = datetime.date.fromtimestamp(time.mktime(time.strptime(revs[0][1], time_format)))
        if first < nadanieUprawnien:
            for b in revs:
                if b[2] not in botNames and b[2] != username:
                    check = 1
                    break
            if check == 0:
                flagLastRev(site, a, 'Automatyczne przeglądanie haseł Richiskiego sprzed ery wersji przejrzanych')
                text = '\n*[[%s]]' % a.title()
                output += text
                file = open('output/%s.txt' % username, 'a')
                file.write(text.encode( "utf-8" ))
                file.close

    for a in lista_stron2:
        revs = a.getVersionHistory(reverseOrder=True)
        check = 0
        first = datetime.date.fromtimestamp(time.mktime(time.strptime(revs[0][1], time_format)))
        if first < nadanieUprawnien:
            for b in revs:
                if b[2] not in botNames and b[2] != username:
                    check = 1
                    break
            if check == 0:
                text = '\n*[[%s]]' % a.title()
                output += text
                file = open('output/%s.txt' % username, 'a')
                file.write(text.encode( "utf-8" ))
                file.close


    outputPage.put(output, comment="Aktualizacja listy (teraz tylko utworzone przed nadaniem uprawnień redaktora")

if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
