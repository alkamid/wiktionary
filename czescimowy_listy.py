#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import Category
from pywikibot import pagegenerators
import re
from pywikibot import xmlreader
import collections
from klasa import *
        
def czescimowy_listy(data):
    locale.setlocale(locale.LC_ALL, 'pl_PL.UTF-8')
    
    data_slownie = data[6] + data[7] + '.' + data[4] + data[5] + '.' + data[0] + data[1] + data[2] + data[3]
    site = pywikibot.getSite()
    notAllowed = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/części_mowy/wszystkie')
    notAllowedPageText = notAllowed.get()
    tempListNotAllowed = notAllowedPageText.split('\n')
    notAllowedSet = set()
    cnt = 1
    for elem in tempListNotAllowed:
        if elem == '|-':
            cnt = 1
        elif cnt == 1:
            notAllowedSet.add(elem[1:])
            cnt = 0
        
    lista = getListFromXML(data)
    gwary = ['{{śląsk}}', '{{gwara}}', '{{góry}}', '{{kielce}}', '{{kraków}}', '{{kresy}}', '{{kujawy}}', '{{lwów}}', '{{mazowsze}}', '{{poznań}}', '{{białystok}}', '{{częstochowa}}', '{{sącz}}', '{{warmia}}', '{{warszawa}}', '{{łódź}}']
    outputSet = set()
    
    for haslo in lista:
        try: h = Haslo(haslo.title, haslo.text)
        except sectionsNotFound:
            pass
        except WrongHeader:
            pass
        else:
            if h.type == 3:    
                for c in h.listLangs:
                    if c.lang == 'polski':
                        c.pola()
                        if c.type not in (2,3,4,5,7,11):
                            for d in c.znaczeniaDetail:
                                if 'czasownik' in d[0] and 'forma' not in d[0] and 'związek' not in d[0] and not any(s in d[1] for s in gwary):
                                    outputSet.add(h.title)
                                    
    outputList = list(outputSet)
    outputSorted = sorted(outputList, cmp=locale.strcoll)
    current = None
    outputText = '{{język linków|polski}}<div style="clear:right; margin-bottom: .5em; float: right; padding: .5em 0 .8em 1.4em;">__TOC__</div>\n'
    for czas in outputSorted:
        if czas[0] != current:
            outputText = outputText.strip(' • ')
            current = czas[0]
            outputText += '\n\n=== %s ===\n' % (czas[0])
        
        outputText += '[[%s]] • ' % czas
        
    outputText = outputText.strip(' • ')
    
    #outputPage.put(pretext + u'\n' + tabelka, comment=u"Aktualizacja listy", botflag=False)
    
    file = open("output/czescimowy_lista.txt", 'w')
    file.write(outputText.encode("utf-8"))
    file.close
    '''
    file = open("output/czescimowy_input.txt", 'w')
    file.write(final_input.encode("utf-8"))
    file.close'''
    
def main():
    czescimowy_listy('20120904')
    
    
if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()