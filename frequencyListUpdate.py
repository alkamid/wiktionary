#!/usr/bin/python
# -*- coding: utf-8 -*-

# szuka danego przez szukany_tekst wyrażenia w hasłach

import codecs
from pywikibot import Category
import pywikibot
from pywikibot import pagegenerators
import re
import config
from pywikibot import xmlreader
from os import environ
from klasa import *

def main():
    
    site = pywikibot.Site()
    files = {}
    table = {}
    file = codecs.open('%soutput/frequencyListPL.txt' % (config.path['scripts']), 'r', 'utf-8')
        
    #table = u'<div class="plainlinks">\n{| border="0"\n! POLSKIE\n! NIEPOLSKIE\n|-\n| valign="top" |'
    table = '\n{| class="wikitable sortable"\n! słowo !! linków '
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
        page = pywikibot.Page(site, tmp[0].strip())
        try: page.get()
        except pywikibot.NoPage:
            pass
        except pywikibot.IsRedirectPage:
            pass
        except pywikibot.InvalidTitle:
            continue
        except TypeError:
            pass
        else:
            if page.namespace():
                continue
            found = 1
            
        if not found:
            if dluga:
                table += '\n|-\n| [[%s]] || %d' % (tmp[0], int(tmp[1]))
            else:
                table += '\n|-\n| [[%s]] || [{{fullurl:Specjalna:Linkujące|limit=500&from=0&target=%s}} %d]' % (tmp[0], tmp[0].replace(' ', '_'), int(tmp[1]))
            i += 1
    
    table += '\n|-\n|}'        

    file = open('%soutput/frequencyProcessedTable.txt' % config.path['scripts'], 'w')
    file.write(table.encode('utf-8'))
    file.close()
    if dluga:
        outputPage = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/listy/Najbardziej_potrzebne_-_długa_lista')
    else:
        outputPage = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/listy/Najbardziej_potrzebne')
    
    outputPage.put(table, comment='aktualizacja')
    
if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
