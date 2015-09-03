#!/usr/bin/python
# -*- coding: utf-8 -*-

# wstawia odpowiedni parametr w językach używających znaków diaktrycznych

import codecs
from pywikibot import Category
import pywikibot
from pywikibot import pagegenerators
import re
from klasa import *

def main():

    site = pywikibot.getSite()

    # mode = 1 - updating pages from recent changes; 2 - after adding new languages to the script, all the words in that language have to be checked
    mode = 1

    mylist = set()
    if mode == 1:
        RClimit = readRCLimit('headerIndexing').strip()
        mylist = RecentChanges(RClimit)
        writeRCLimit('headerIndexing')
    if mode == 2:
        newlangs = ['arabski', 'perski', 'paszto', 'dari', 'urdu', 'osmańsko-turecki']
        for elem in newlangs:
            cat = Category(site, 'Kategoria:%s (indeks)' % elem)
            pageSet = set(pagegenerators.CategorizedPageGenerator(cat))
            for page in pageSet:
                mylist.add(page.title())


    replace = {}
    replace['arabski'] = {'إ': 'ا', 'آ': 'ا', 'ا': 'ا', 'أ': 'ا'}
    replace['dari'] = {'إ': 'ا', 'آ': 'ا', 'ا': 'ا', 'أ': 'ا'}
    replace['francuski'] = {'À': 'A', 'Â': 'A', 'Ç': 'C', 'É': 'E', 'È': 'E', 'Ë': 'E', 'Ê': 'E', 'Î': 'I', 'Ï': 'I', 'Ô': 'O', 'Œ': 'OE', 'Ù': 'U', 'Ú': 'U', 'Û': 'U', 'à': 'a', 'â': 'a', 'ç': 'c', 'é': 'e', 'è': 'e', 'ë': 'e', 'ê': 'e', 'î': 'i', 'ï': 'i', 'ô': 'o', 'œ': 'oe', 'ù': 'u', 'ú': 'u', 'û': 'u'}
    replace['hiszpański'] = {'Á': 'A','É': 'E','Í': 'I','Ó': 'O','Ú': 'U','á': 'a','é': 'e','í': 'i','ó': 'o','ú': 'u'}
    #replace[u'kurdyjski'] = {u'É': u'E', u'Í': u'I', u'Ú': u'U', u'Ù': u'U', u'é': u'e', u'í': u'i', u'ú': u'u', u'ù': u'u'}
    replace['nowogrecki'] = {'Ά': 'Α', 'Έ': 'Ε', 'Ή': 'Η', 'Ί': 'Ι', 'Ϊ': 'Ι', 'Ό': 'Ο', 'Ύ': 'Υ', 'Ϋ': 'Υ', 'Ώ': 'Ω', 'ά': 'α', 'έ': 'ε', 'ί': 'ι', 'ϊ': 'ι', 'ΐ': 'ι', 'ό': 'ο', 'ύ': 'υ', 'ϋ': 'υ', 'ΰ': 'υ', 'ώ': 'ω', 'ή': 'η', 'ς': 'σ'}
    replace['osmańsko-turecki'] = {'إ': 'ا', 'آ': 'ا', 'ا': 'ا', 'أ': 'ا'}
    replace['perski'] = {'إ': 'ا', 'آ': 'ا', 'ا': 'ا', 'أ': 'ا'}
    replace['paszto'] = {'إ': 'ا', 'آ': 'ا', 'ا': 'ا', 'أ': 'ا'}
    replace['urdu'] = {'إ': 'ا', 'آ': 'ا', 'ا': 'ا', 'أ': 'ا'}
    #replace[u'wietnamski'] = {u'Ă': u'A', u'Â': u'A', u'Đ': u'D', u'Ê': u'E', u'Ô': u'O', u'Ơ': u'O', u'Ư': u'U', u'ă': u'a', u'â': u'a', u'đ': u'd', u'ê': u'e', u'ô': u'o', u'ơ': u'o', u'ư': u'u'}

    for mytitle in mylist:
        try: h = Haslo(mytitle)
        except sectionsNotFound:
            pass
        except WrongHeader:
            pass
        else:
            if h.type == 3:
                change = 0
                for c in h.listLangs:
                    try: c.lang
                    except AttributeError:
                        pass
                    else:
                        if c.lang in replace:
                            first = c.title
                            temp = c.title
                            for rep in replace[c.lang]:
                                temp = temp.replace(rep, replace[c.lang][rep])
                            if first != temp:
                                c.headerArg = temp
                                c.updateHeader()
                                change = 1

                if change:
                    h.push(False, 'modyfikacja nagłówka w celu poprawnego indeksowania haseł (usunięcie znaków diakrytycznych)')


if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
