#!/usr/bin/python
# -*- coding: utf-8 -*-

import wikipedia
import catlib
import pagegenerators
import re
import xmlreader
import collections
from klasa import *
        
def czescimowy_listy(data):
    locale.setlocale(locale.LC_ALL, 'pl_PL.UTF-8')
    
    data_slownie = data[6] + data[7] + u'.' + data[4] + data[5] + u'.' + data[0] + data[1] + data[2] + data[3]
    site = wikipedia.getSite()
    notAllowed = wikipedia.Page(site, u'Wikipedysta:AlkamidBot/części_mowy/wszystkie')
    notAllowedPageText = notAllowed.get()
    tempListNotAllowed = notAllowedPageText.split(u'\n')
    notAllowedSet = set()
    cnt = 1
    for elem in tempListNotAllowed:
        if elem == u'|-':
            cnt = 1
        elif cnt == 1:
            notAllowedSet.add(elem[1:])
            cnt = 0
        
    lista = getListFromXML(data)
    gwary = [u'{{śląsk}}', u'{{gwara}}', u'{{góry}}', u'{{kielce}}', u'{{kraków}}', u'{{kresy}}', u'{{kujawy}}', u'{{lwów}}', u'{{mazowsze}}', u'{{poznań}}', u'{{białystok}}', u'{{częstochowa}}', u'{{sącz}}', u'{{warmia}}', u'{{warszawa}}', u'{{łódź}}']
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
                    if c.lang == u'polski':
                        c.pola()
                        if c.type not in (2,3,4,5,7,11):
                            for d in c.znaczeniaDetail:
                                if u'czasownik' in d[0] and u'forma' not in d[0] and u'związek' not in d[0] and not any(s in d[1] for s in gwary):
                                    outputSet.add(h.title)
                                    
    outputList = list(outputSet)
    outputSorted = sorted(outputList, cmp=locale.strcoll)
    current = None
    outputText = u'{{język linków|polski}}<div style="clear:right; margin-bottom: .5em; float: right; padding: .5em 0 .8em 1.4em;">__TOC__</div>\n'
    for czas in outputSorted:
        if czas[0] != current:
            outputText = outputText.strip(u' • ')
            current = czas[0]
            outputText += u'\n\n=== %s ===\n' % (czas[0])
        
        outputText += u'[[%s]] • ' % czas
        
    outputText = outputText.strip(u' • ')
    
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
        wikipedia.stopme()