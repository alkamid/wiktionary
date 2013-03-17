#!/usr/bin/python
# -*- coding: utf-8 -*-

# wstawia odpowiedni parametr w językach używających znaków diaktrycznych

import codecs
import catlib
import wikipedia
import pagegenerators
import re
from klasa import *

def main():
    
    site = wikipedia.getSite()
    
    # mode = 1 - updating pages from recent changes; 2 - after adding new languages to the script, all the words in that language have to be checked
    mode = 1
    
    mylist = set()
    if mode == 1:
        RClimit = readRCLimit(u'headerIndexing').strip()
        mylist = RecentChanges(RClimit)
        writeRCLimit(u'headerIndexing')
    if mode == 2:
        newlangs = [u'arabski', u'perski', u'paszto', u'dari', u'urdu', u'osmańsko-turecki']
        for elem in newlangs:
            cat = catlib.Category(site, u'Kategoria:%s (indeks)' % elem)
            pageSet = set(pagegenerators.CategorizedPageGenerator(cat))
            for page in pageSet:
                mylist.add(page.title())
    
    
    replace = {}
    replace[u'arabski'] = {u'إ': u'ا', u'آ': u'ا', u'ا': u'ا', u'أ': u'ا'}
    replace[u'dari'] = {u'إ': u'ا', u'آ': u'ا', u'ا': u'ا', u'أ': u'ا'}
    replace[u'francuski'] = {u'À': u'A', u'Â': u'A', u'Ç': u'C', u'É': u'E', u'È': u'E', u'Ë': u'E', u'Ê': u'E', u'Î': u'I', u'Ï': u'I', u'Ô': u'O', u'Œ': u'OE', u'Ù': u'U', u'Ú': u'U', u'Û': u'U', u'à': u'a', u'â': u'a', u'ç': u'c', u'é': u'e', u'è': u'e', u'ë': u'e', u'ê': u'e', u'î': u'i', u'ï': u'i', u'ô': u'o', u'œ': u'oe', u'ù': u'u', u'ú': u'u', u'û': u'u'}
    replace[u'hiszpański'] = {u'Á': u'A',u'É': u'E',u'Í': u'I',u'Ó': u'O',u'Ú': u'U',u'á': u'a',u'é': u'e',u'í': u'i',u'ó': u'o',u'ú': u'u'}
    #replace[u'kurdyjski'] = {u'É': u'E', u'Í': u'I', u'Ú': u'U', u'Ù': u'U', u'é': u'e', u'í': u'i', u'ú': u'u', u'ù': u'u'}
    replace[u'nowogrecki'] = {u'Ά': u'Α', u'Έ': u'Ε', u'Ή': u'Η', u'Ί': u'Ι', u'Ϊ': u'Ι', u'Ό': u'Ο', u'Ύ': u'Υ', u'Ϋ': u'Υ', u'Ώ': u'Ω', u'ά': u'α', u'έ': u'ε', u'ί': u'ι', u'ϊ': u'ι', u'ΐ': u'ι', u'ό': u'ο', u'ύ': u'υ', u'ϋ': u'υ', u'ΰ': u'υ', u'ώ': u'ω', u'ή': u'η', u'ς': u'σ'}
    replace[u'osmańsko-turecki'] = {u'إ': u'ا', u'آ': u'ا', u'ا': u'ا', u'أ': u'ا'}
    replace[u'perski'] = {u'إ': u'ا', u'آ': u'ا', u'ا': u'ا', u'أ': u'ا'}
    replace[u'paszto'] = {u'إ': u'ا', u'آ': u'ا', u'ا': u'ا', u'أ': u'ا'}
    replace[u'urdu'] = {u'إ': u'ا', u'آ': u'ا', u'ا': u'ا', u'أ': u'ا'}
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
                    h.push(False, u'modyfikacja nagłówka w celu poprawnego indeksowania haseł (usunięcie znaków diakrytycznych)')
    
            
if __name__ == '__main__':
    try:
        main()
    finally:
        wikipedia.stopme()