#!/usr/bin/python
#-*- coding: utf-8 -*-

from klasa import *
import collections
from pyuca import Collator

def aTergo(date):

    site = pywikibot.getSite()
    c = Collator('allkeys.txt')
    pageList = getListFromXML(date) # if not called from afterDump.py, it can be changed to getListFromXML('foo', True) - will fetch the latest dump

    sortDict = collections.defaultdict()
    sortedDict = collections.defaultdict()

    #sweep through the dump and add reversed words to appropriate dictionaries
    for elem in pageList:
        try: page = Haslo(elem.title, elem.text) #use the parser in klasa.py to parse xml entry
        except sectionsNotFound:
            continue
        except WrongHeader:
            continue
        else:
            if page.type == 3:
                for section in page.listLangs:
                    if section.lang in sortDict:
                        sortDict[section.lang].append(page.title[::-1])
                    else:
                        sortDict[section.lang] = [page.title[::-1]]


    sortedDict['afrykanerski'] = sorted(sortDict['afrykanerski'], key=c.sort_key)
    letter = sortedDict['afrykanerski'][0][0]
    text = '{| class=hiddentable style="text-align:right"\n|-'
    counter = 0
    for i in range(len(sortedDict['afrykanerski'])):

        if elem[0] == letter:
            text = text + '|[[%s|%s]]|\n' % (elem[::-1], elem)
        else:
            pywikibot.Page(site, 'Wikipedysta:Alkamid/atergo/afrykanerski/%s' % letter).put(text)
            text = ''
            letter = elem[0]
            text = text + '* %s\n' % elem
