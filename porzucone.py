#!/usr/bin/python
# -*- coding: utf-8 -*-

# robienie listy haseł polskich bez wymowy

import codecs
from pywikibot import Category
import pywikibot
from pywikibot import pagegenerators
import re
import math
import datetime
import config

def main():

    site = pywikibot.Site()

    cat_allpages = Category(site,'Kategoria:polski (indeks)')
    cat_dialects = Category(site, 'Kategoria:Polski_(dialekty_i_gwary)')

    list_allpages = pagegenerators.CategorizedPageGenerator(cat_allpages)
    list_dialects = set(pagegenerators.CategorizedPageGenerator(cat_dialects, recurse=True))

    lista = []
    count_all = 0
    
    final = ('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n'
             '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
             '<html xmlns="http://www.w3.org/1999/xhtml\nxml:lang="pl">\n'
             '<head>\n<meta http-equiv="content-type" content="text/html; charset=UTF-8" />\n'
             '</head><body>')
    
    final += ('Poniżej znajduje się lista polskich haseł, do których '
              'nie linkuje nic oprócz stron z przestrzeni nazw Wikipedysta. W związku '
              'z tym trudno trafić do takiego hasła inaczej niż przez bezpośrednie jego '
              'wyszukanie. Jeśli możesz, dodaj w innym haśle odnośnik do porzuconego '
              'słowa, np. w przykładach lub pokrewnych.')
    
    final_lista = ''

    wykluczone = set(pagegenerators.AllpagesPageGenerator(namespace=2)) # namespace User

    for page in list_allpages:
        if page not in list_dialects:
            try:
                strona = pywikibot.Page(site, page.title())
            except pywikibot.Error:
                print('error')
            else:
                pages = set(a for a in strona.getReferences())
                for b in wykluczone:
                    try: pages.remove(b)
                    except ValueError:
                        continue
                if strona in pages:
                    pages.remove(strona)
                if not pages:
                    dodaj = '\n<br /><a href="http://pl.wiktionary.org/wiki/%s">%s</a>' % (strona.title(), strona.title())
                    final_lista = final_lista + dodaj
                    count_all = count_all + 1


    data = datetime.datetime.now() + datetime.timedelta(hours=2)
    data1 = data.strftime("Ostatnia aktualizacja listy: %Y-%m-%d, %H:%M:%S")

    final = final + data1 + '<br />: Licznik porzuconych: %d' % count_all
    final = final + final_lista
    final = final + '</body></html>'

    file = open('%spublic_html/porzucone.html' % (config.path['home']), 'w')
    file.write(final)
    file.close

if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
