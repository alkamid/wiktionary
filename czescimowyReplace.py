#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import Category
from pywikibot import pagegenerators
import re
from pywikibot import xmlreader
import collections
from klasa import *
import config

#uwagi wstępne
#nie można zmieniać ''przymiotnik -> ''przymiotnik'', bo będą niepożądane zmiany, ewentualnie można byłoby szukać ''przymiotnik\n i zmieniać, ale struktura hasła w parserze jest taka, że to \n nie wchodzi do zmiennej

        
def czescimowyReplace():

    site = pywikibot.getSite()
    inp = codecs.open('%soutput/czescimowy_input.txt' % config.path['scripts'], encoding='utf-8')
    replacePage = pywikibot.Page(site, u'Wikipedysta:AlkamidBot/części_mowy/zamiana')
    replacePageText = replacePage.get()
    tempListReplace = replacePageText.split(u'\n')
    replaceList = []
    cnt = 0
    for elem in tempListReplace:
        if elem == u'|-':
            old = ''
            new = ''
            cnt = 1
        if cnt == 1:
            cnt += 1
        elif cnt == 2:
            old = elem[1:]
            cnt += 1
        elif cnt == 3:
            new = elem[1:]
            replaceList.append([old, new])
            cnt = 1
    
    #for replaceText in replaceList:
    #    print replaceText[0]
    #    print replaceText[1]
            
    for line in inp:
        if line:
            try: h = Haslo(line)
            except sectionsNotFound:
                pass
            except pywikibot.InvalidTitle:
                pass
            except AttributeError:
                pass
            else:
                #print h.title
                if h.type == 3:
                    changed = 0
                    for c in h.listLangs:
                        c.pola()
                        if c.type not in (2,3,4,5,7,11):
                            for d in c.znaczeniaDetail:
                                temp = d[0]
                                for replaceText in replaceList:
                                    d[0] = d[0].replace(replaceText[0], replaceText[1])
                                    if d[0] != temp:
                                        c.saveChanges()
                                if d[0] != temp:
                                    changed = 1
                    if changed:
                        h.push(myComment=u'automatyczne porządkowanie części mowy wg [[Wikipedysta:AlkamidBot/części_mowy/zamiana]]')
