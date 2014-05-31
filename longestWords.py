#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
from pywikibot import Category
import pywikibot
from pywikibot import pagegenerators
import re
from pywikibot import xmlreader
from klasa import *

def main():
    
    data = u'20120325'
    lista_stron2 = getListFromXML(data)
    
    ranking = []
    #for line in t:
    #    ranking.append(line.strip())
    
    
    for a in lista_stron2:            
        #if int(a.revisionid) > 2646076 and a.username not in ('Olafbot', 'AlkamidBot', 'KamikazeBot', 'MastiBot', 'Luckas-bot', 'Agnese'):
        try: h = Haslo(a.title, a.text)
        except sectionsNotFound:
            pass
        except WrongHeader:
            pass
        else:
            if h.type == 3:    
                for elem in h.listLangs:
                    if elem.lang == 'afrykanerski':
                        ranking.append([a.title, len(elem.content)])                        
    
    def sortkey(row):
        return float(row[1])
        
    ranking.sort(key=sortkey, reverse=True)
    for i in range(50):
        print u'[[%s]]' % ranking[i][0]

    
    #for p in lista_stron2:
    #    if any (item in p.text for item in lista):
    #        print u'*[[%s]]' % p.title
            
if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
