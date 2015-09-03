#!/usr/bin/python
# -*- coding: utf-8 -*-

# under construction - ma ułatwić mi wprowadzanie słów

import sys
sys.path.append('/home/adam/pywiki/pywikipedia')
import codecs

def main():
    tom = 1
    lista = []
    inp = codecs.open('input.txt', encoding='utf-8')

    for line in inp:
        lista.append(line.split('@'))

    filename = "output_dododania.txt"

    file = open(filename, 'w')

    for haslo in lista:
        text = '== %s ({{język francuski}}) ==\n{{wymowa}}' % (haslo[0])

        if (haslo[2]!='0'):
            text = text + ' {{IPA3|%s}}' % (haslo[2])

        text = text + '\n{{znaczenia}}\n'

        if (haslo[1] == 'nm'):
            text = text + '\'\'rzeczownik, rodzaj męski\'\'\n'
        if (haslo[1] == 'nż'):
            text = text + '\'\'rzeczownik, rodzaj żeński\'\'\n'
        if (haslo[1] == 'adv'):
            text = text + '\'\'przysłówek\'\'\n'

        text = text + ': (1.1) %s<ref>{{WP2003|tom=%s|strony=%s}}</ref>' % (haslo[3], tom, haslo[4])
        text = text + '\n{{odmiana}}\n{{przykłady}}\n: (1.1)\n{{składnia}}\n{{kolokacje}}\n{{synonimy}}\n'
        if (haslo[5]!='0'):
            text = text + ': (1.1) %s\n' % (haslo[5])
        text = text + '{{antonimy}}\n'
        if (haslo[6]!='0'):
            text = text + ': (1.1) %s\n' % (haslo[6])
        text = text + '{{pokrewne}}\n{{frazeologia}}\n{{etymologia}}'
        if (haslo[7]!='0'):
            text = text + ' {{etym|%s}}' % (haslo[7])
        text = text + '\n{{uwagi}}\n{{źródła}}\n<references/>'

        file.write(text.encode( "utf-8" ))

    file.close

if __name__ == '__main__':
    main()
