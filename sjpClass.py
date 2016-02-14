#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot

class kategoriaSlowa():
    def __init__(self, name, counter, pages, tabelka, outputFile):
        self.name = name
        self.counter = counter
        self.pages = 'Wikipedysta:AlkamidBot/sjp/' + pages
        self.buffer = ''
        self.tabelka = tabelka
        self.outputFile = 'output/' + outputFile
        self.limit = 0
    def addLimit(self, limit):
        self.limit = limit

def checkHistory(pagename):
    #returns 1, if AlkamidBot or Olafbot were the last authors, 0 if someone is verifying the page (=it was last edited by someone else)

    bots = ('AlkamidBot', 'Olafbot', 'PBbot')

    site = pywikibot.getSite()
    page = pywikibot.Page(site, pagename)
    try: page.get()
    except pywikibot.NoPage:
        return 1
    else:
        history = page.getVersionHistory()
        if history[0][2] in bots:
            return 1
        else:
            return 0
