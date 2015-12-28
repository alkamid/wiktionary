#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
import pywikibot as pwb
import config
from klasa import *

def frequencyListUpdate():

    site = pwb.Site()
    table = {}

    table = '\n{| class="wikitable sortable"\n! słowo !! linków '

    i=1
    dluga = 0 # mozna wygenerowac dluga liste, ktora bedzie zapisywala sie na stronie /Najbardziej potrzebne - dluga lista
    if dluga:
        limit = 20000
    else:
        limit = 500

    with open('{0}output/frequencyListPL.txt'.format(config.path['scripts']), encoding='utf-8', mode='r') as f:

        for line in f:
            if i>limit:
                break
            tmp = line.split('=')

            found = 0
            page = pwb.Page(site, tmp[0].strip())
            try: page.get()
            except pwb.NoPage:
                pass
            except pwb.IsRedirectPage:
                pass
            except pwb.InvalidTitle:
                continue
            except TypeError:
                pass
            else:
                if page.namespace():
                    continue
                found = 1

            if not found:
                if dluga:
                    table += '\n|-\n| [[{0}]] || {1}'.format(tmp[0], int(tmp[1]))
                else:
                    table += '\n|-\n| [[{0}]] || [{{fullurl:Specjalna:Linkujące|limit=500&from=0&target={1}}} {2}]'.format(tmp[0], tmp[0].replace(' ', '_'), int(tmp[1]))
                i += 1

    table += '\n|-\n|}'

    with open('{0}output/frequencyProcessedTable.txt'.format(config.path['scripts']), encoding='utf-8', mode='w') as g:
        g.write(table)

    if dluga:
        outputPage = pwb.Page(site, 'Wikipedysta:AlkamidBot/listy/Najbardziej_potrzebne_-_długa_lista')
    else:
        outputPage = pwb.Page(site, 'Wikipedysta:AlkamidBot/listy/Najbardziej_potrzebne')

    outputPage.text = table
    outputPage.save(summary='aktualizacja')

if __name__ == '__main__':
    try:
        frequencyListUpdate()
    finally:
        pwb.stopme()
