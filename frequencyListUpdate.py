#!/usr/bin/python
# -*- coding: utf-8 -*-

# szuka danego przez szukany_tekst wyrażenia w hasłach

import codecs
import catlib
import wikipedia
import pagegenerators
import re
import xmlreader
from os import environ
from klasa import *

def main():
    
    site = wikipedia.getSite()
    files = {}
    table = {}
    file = codecs.open(u'%s/wikt/moje/output/frequencyListPL.txt' % (environ['HOME']), 'r', 'utf-8')
        
    #table = u'<div class="plainlinks">\n{| border="0"\n! POLSKIE\n! NIEPOLSKIE\n|-\n| valign="top" |'
    table = u'\n{| class="wikitable sortable"\n! słowo !! linków '
    #table['rest'] = u'\n{| class="wikitable sortable"\n! słowo !! linków '
    
    i=1
    dluga = 0 # mozna wygenerowac dluga liste, ktora bedzie zapisywala sie na stronie /Najbardziej potrzebne - dluga lista
    if dluga:
        limit = 20000
    else:
        limit = 500
    
    for line in file:
        if i>limit:
            break
        tmp = line.split('=')

        found = 0
        page = wikipedia.Page(site, tmp[0].strip())
        try: page.get()
        except wikipedia.NoPage:
            pass
        except wikipedia.IsRedirectPage:
            pass
        except wikipedia.InvalidTitle:
            continue
        except TypeError:
            pass
        else:
            if page.namespace():
                continue
            found = 1
            
        if not found:
            if dluga:
                table += u'\n|-\n| [[%s]] || %d' % (tmp[0], int(tmp[1]))
            else:
                table += u'\n|-\n| [[%s]] || [{{fullurl:Specjalna:Linkujące|limit=500&from=0&target=%s}} %d]' % (tmp[0], tmp[0].replace(u' ', u'_'), int(tmp[1]))
            i += 1
    
    table += u'\n|-\n|}'        

    file = open(u'%s/wikt/moje/output/frequencyProcessedTable.txt' % environ['HOME'], 'w')
    file.write(table.encode('utf-8'))
    file.close()
    if dluga:
        outputPage = wikipedia.Page(site, u'Wikipedysta:AlkamidBot/listy/Najbardziej_potrzebne_-_długa_lista')
    else:
        outputPage = wikipedia.Page(site, u'Wikipedysta:AlkamidBot/listy/Najbardziej_potrzebne')
    
    outputPage.put(table, comment='aktualizacja')
    
if __name__ == '__main__':
    try:
        main()
    finally:
        wikipedia.stopme()