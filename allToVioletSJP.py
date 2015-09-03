#!/usr/bin/python
# -*- coding: utf-8 -*-

# z listy wszystkich potrzebnych (od sp5uhe) tworzy listę czerwonych i fioletowych

import codecs
import urllib.request, urllib.error, urllib.parse
import urllib.request, urllib.parse, urllib.error
import pywikibot
from lxml import html
from klasa import *

def main():

    site = pywikibot.getSite()
    lista = []

    filename_input = 'potrzebne.txt'
    filename_temp = 'potrzebneTemp.txt'
    filename_output = 'potrzebneBot.txt'

    inp = codecs.open('/home/alkamid/wikt/moje/importsjp/%s' % (filename_input), encoding='utf-8')



    i = 1
    for line in inp:
        line = line.strip()
        while True:
            try: web = html.parse('http://www.sjp.pl/%s' % urllib.parse.quote(line.encode('utf-8')))
            except IOError:
                break
            break

        try: brak = web.xpath('//p/text()')
        except AssertionError:
            continue
        print(i)
        text = ''
        if brak and brak[0] != 'słowo nie występuje w słowniku' and brak[0] != 'słowo występuje w słowniku tylko jako część innych haseł':
            text = line + '\n'
            file = open('importsjp/%s' % (filename_temp), 'a')
            file.write(text.encode( "utf-8" ))
            file.close
        i += 1

    inp.close

    inp = codecs.open('/home/alkamid/wikt/moje/importsjp/%s' % (filename_temp), encoding='utf-8')
    file = open('importsjp/%s' % (filename_output), 'a')

    i = 1
    for line in inp:
        print(i)
        i += 1
        text = ''
        line = line.strip()

        page = pywikibot.Page(site, line)

        haslo = Haslo(line)

        if haslo.type == 5:
            continue
        else:
            if haslo.type == 1:
                text = line + '\n'
                file.write(text.encode( "utf-8" ))
            if haslo.type == 3:
                found = 0
                for a in haslo.listLangs:
                    if 'język polski' in a.langLong or 'termin obcy' in a.langLong or 'użycie międzynarodowe' in a.langLong:
                        found = 1

                if not found:
                #if u'á' not in line and u'é' not in line and u'í' not in line and u'ñ' not in line and u'ü' not in line and u'à' not in line and u'â' not in line and u'é' not in line and u'è' not in line and u'ê' not in line and u'ë' not in line and u'î' not in line and u'ï' not in line and u'ô' not in line and u'ä' not in line and u'ö' not in line and u'ü' not in line and u'ß' not in line and u'æ' not in line and u'ø' not in line and u'ö' not in line and u'ä' not in line and u'å' not in line and u'š' not in line and u'ă' not in line and u'ī' not in line and u'\'' not in line:
                    text = line + '\n'
                    file.write(text.encode( "utf-8" ))

    file.close
    inp.close

if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
