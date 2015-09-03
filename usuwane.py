#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot

def getDeletedList():
    deleted = set()
    site = pywikibot.Site()
    pageDeleted = pywikibot.Page(site, 'Wikisłownik:Ranking brakujących tłumaczeń/zawsze usuwane')
    for line in pageDeleted.get().split('\n'):
        if line[0] == ':':
            lineList = line.split('[[')
            deleted.add(lineList[1].strip(']'))
    return deleted

print(getDeletedList())
