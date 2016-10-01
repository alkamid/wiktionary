#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators
import re
from pywikibot import xmlreader
import collections
import codecs
from klasa import *
from importsjp import *

def addFromList(iterable):
    for elem in iterable:
        try: word = Haslo(elem[0])
        except sectionsNotFound:
            pass
        except WrongHeader:
            pass
        else:
            if word.type == 3:
                for lang in word.listLangs:
                    print(lang.type)
                    if lang.type == 1:
                        lang.pola()
                        if lang.type == 9:
                            change = 0
                            for d in lang.znaczeniaDetail:
                                if 'rzeczownik' in d[0] and '{{forma rzeczownika' not in d[0] and 'odrzeczownikowy' not in d[0] and 'rodzaj' not in d[0]:
                                    d[0] = elem[1]
                                    lang.saveChanges()
                word.push(False, 'uzupełnienie rodzaju na podstawie [[Wikipedysta:Adam/rodzaje_-_polski|listy Adama]]')

def addPlGender(iterable):
    odmOlafa = OdmianaOlafa()
    for elem in iterable:
        page = HasloSJP(elem, True)
        print(elem)
        if page.type:
            diff = 0
            tempList = []
            for b in page.words:
                print('\'%s\' - \'%s\'' % (elem, b.title))
                if b.title == elem:
                    print('jestem')
                    b.flexTable(odmOlafa)
                    tempList.append(b)

            if not len(tempList):
                continue
            else:
                temp = tempList[0].typeText
                if '{{brak' in temp:
                    continue
                for c in tempList:
                    if c.title == elem and c.typeText != temp:
                        diff = 1
                if not diff:
                    try: word = Haslo(elem)
                    except sectionsNotFound:
                        pass
                    except WrongHeader:
                        pass
                    else:
                        if word.type == 3:
                            for lang in word.listLangs:
                                if lang.lang == 'polski':
                                    lang.pola()
                                    if lang.type != 7:
                                        change = 0
                                        for d in lang.znaczeniaDetail:
                                            temp_d = d[0]
                                            d[0] = d[0].replace('\'\'rzeczownik\'\'', temp)
                                            if temp_d != d[0]:
                                                change = 1
                                        if change:
                                            lang.saveChanges()
                            word.push(False, myComment='dodanie rodzaju; źródła: sjp.pl, Morfeusz')

def main():
    '''file = codecs.open(u'/home/adam/wikt/moje/input/rodzajenowe.txt', encoding='utf-8')
    output = u''
    for line in file:
        if line[0].isupper():
            output += line[0].upper() + line[1:].strip('\n') + u', nazwa własna\n'
        else:
            output += line
    file.close

    file = open(u'/home/adam/wikt/moje/input/rodzajenowe1.txt', 'w')
    file.write(output.encode( "utf-8" ))
    file.close'''

    file = codecs.open('/home/adam/wikt/moje/input/rodzajenowe1.txt', encoding='utf-8')
    listAdam = []
    for line in file:
        tmp = line.strip().split(' → ')
        tmp[1] = '\'\'%s\'\'' % tmp[1]
        listAdam.append(tmp)

    addFromList(listAdam)
    '''
    file = codecs.open(u'/home/adam/wikt/moje/input/polskieczesci.txt', encoding='utf-8')
    list = []
    for line in file:
        list.append(line.strip())

    addPlGender(list)'''

if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
