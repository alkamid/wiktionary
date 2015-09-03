#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot

def test():
    site = pywikibot.getSite('pl', 'wiktionary')
    page = pywikibot.Page(site, 'cool')
    print((page.get()))

test()
