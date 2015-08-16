#!/usr/bin/python
# -*- coding: utf-8 -*-

# z listy wszystkich potrzebnych (od sp5uhe) tworzy listę czerwonych i fioletowych

from klasa import *

def main():
    lista = ['握']
    for a in lista:
        h = Haslo(a)
        #print h.content
        print(h.type)
        print(h.listLangs[1].type)
        h.listLangs[1].pola()
        print(h.listLangs[1].type)
        #if h.type == 3:
        #       b = h.listLangs[1]
        #       b.pola()
        #       print b.type

if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
