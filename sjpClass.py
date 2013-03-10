#!/usr/bin/python
# -*- coding: utf-8 -*-

import wikipedia

class kategoriaSlowa():
    def __init__(self, name, counter, pages, tabelka, outputFile):
        self.name = name
        self.counter = counter
        self.pages = u'Wikipedysta:AlkamidBot/sjp/' + pages
        self.buffer = u''
        self.tabelka = tabelka
        self.outputFile = u'output/' + outputFile
        self.limit = 0
    def addLimit(self, limit):
        self.limit = limit

def checkHistory(pagename):
    #returns 1, if AlkamidBot or Olafbot were the last authors, 0 if someone is verifying the page (=it was last edited by someone else)
    site = wikipedia.getSite()
    page = wikipedia.Page(site, pagename)
    try: page.get()
    except wikipedia.NoPage:
        return 1
    else:
        history = page.getVersionHistory()
        if history[0][2] == 'AlkamidBot' or history[0][2] == 'Olafbot':
            return 1
        else:
            return 0