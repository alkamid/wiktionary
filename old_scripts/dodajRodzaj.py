#!/usr/bin/python
# -*- coding: utf-8 -*-

# wprowadza rodzaj do haseł z listy w formacie "hasło → nowy rodzaj"

from klasa import *
import codecs


def main():
    inp = codecs.open('input/rodzaje.txt', encoding='utf-8')
    lst = []
    for line in inp:
        line = line.split(' → ')
        h = Haslo(line[0])

        if h.type == 3:
            print(len(h.content))
            for b in h.listLangs:
                b.pola()
                print(b.title)
                if b.lang == 'polski' and b.type != 7 and b.znaczeniaDetail:
                    for c in b.znaczeniaDetail:
                        if c[0] == '\'\'rzeczownik\'\'' or c[0] == '\'\'rzeczownik, nazwa własna\'\'':
                            c[0] = '\'\'' + line[1].strip() + '\'\''
            for b in h.listLangs:
                b.saveChanges()
            h.push(False, 'dodanie rodzaju po ręcznym sprawdzeniu [[Wikipedysta:Adam/rodzaje_-_polski|listy Adama]]')
            #print h.push()
if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
