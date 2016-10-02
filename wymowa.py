# -*- coding: utf-8 -*-

'''
generate a list of Polish words lacking pronunciation; output written to Wikipedysta:AlkamidBot/wymowa and wymowa.txt
groups pages in four categories:
1. starting with a capital letter
2. not 1
3. foreign word in Polish use
4. a list generated from the most visited pages
'''

import os
from pywikibot import Category
import pywikibot
from pywikibot import pagegenerators
import re
import datetime
import urllib.error
import config
from klasa import *
from external.pageviews import PageviewsClient
from utils import get_nonmain_namespaces

def main():

    #get the most popular pages (generated by PageviewAPI)
    p = PageviewsClient()
    ns = get_nonmain_namespaces('pl.wiktionary')
    top = p.top_articles('pl.wiktionary', limit=1000)
    top_main = [{'article': a['article'], 'views': a['views'],\
                 'rank': a['rank']} for a in top if not\
                any(a['article'].startswith(prefix + ':') for prefix in ns)]
    popular_list = [a['article'] for a in top_main]

    #get a list of archaic words from XML dump
    listArchaic = set()
    outputArchaic = set()
    re_arch = re.compile(r'{{przest}}')
    re_numMeans = re.compile(r': \([0-9]\.[0-9]\)')
    pageList = getListFromXML('xxx', True)

    #below we search for all the words that are purely archaic, i.e. all its meanings have {{przest}} template. I don't know if it's not an overkill -- we could just fetch a Category?
    for page in pageList:
        if '{{przest}}' in page.text:
            try: word = Haslo(page)
            except sectionsNotFound:
                pass
            except WrongHeader:
                pass
            else:
                if word.type == 3:
                    for lang in word.listLangs:
                        if lang.lang == 'polski':
                            lang.pola()
                            if lang.type == 1:
                                s_arch = re.findall(re_arch, lang.subSections['znaczenia'].text)
                                s_numMeans = re.findall(re_numMeans, lang.subSections['znaczenia'].text)
                                if len(s_arch) == len(s_numMeans):
                                    listArchaic.add(word.title)

    site = pywikibot.Site()
    siteCommons = pywikibot.Site('commons', 'commons')

    cat_main = Category(site,'Kategoria:polski (indeks)')
    cat_gwary = Category(site, 'Kategoria:Polski_(dialekty_i_gwary)')
    cat_obce = Category(site, 'Kategoria:polski_-_terminy_obce_(indeks)')

    output_main = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/wymowa')
    output_gwary = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/wymowa/gwary')
    output_r = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/wymowa/bez_r')
    output_stat = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/wymowa/stat')

    lista_main = pagegenerators.CategorizedPageGenerator(cat_main)
    lista_gwary = set(page.title() for page in pagegenerators.CategorizedPageGenerator(cat_gwary, recurse=True))
    lista_obce = set(page.title() for page in pagegenerators.CategorizedPageGenerator(cat_obce))

    re_ipa = re.compile('\{\{język polski\}\}\) \=\=.*?\{\{IPA3.*?(\=|)', re.DOTALL)
    re_r = re.compile('r([^z]|$)')

    final = ''
    r = ''
    with_r = set()

    lista = set()
    outputGwary = set()
    outputObce = set()
    lista_ipa = set()
    lista_wielkie = set()
    lista_male = set()
    outputPopular = ''
    count_jest = 0
    count_brak = 0
    count_all = 0

    for page in lista_main:
        title = page.title()
        try:
            pywikibot.page.FilePage(siteCommons, 'Pl-%s.ogg' % page.title()).fileIsShared()
        except (pywikibot.exceptions.NoPage):
            try:
                pywikibot.page.FilePage(siteCommons, 'Pl-%s.OGG' % page.title()).fileIsShared()
            except (pywikibot.exceptions.NoPage):
                count_brak += 1
                if title in lista_gwary:
                    outputGwary.add(title)
                elif title in listArchaic:
                    outputArchaic.add(title)
                elif title in lista_obce:
                    outputObce.add(title)
                else:
                    try: s_ipa = re.search(re_ipa, page.get())
                    except (urllib.error.HTTPError, pywikibot.exceptions.NoPage, pywikibot.exceptions.IsRedirectPage):
                        pass
                    else:
                        if s_ipa == None:
                            lista_ipa.add(title)
                        else:
                            lista.add(title)
            else:
                count_jest = count_jest + 1
        else:
            count_jest = count_jest + 1
        count_all = count_all + 1


    for a in lista:
        if a[0].isupper():
            lista_wielkie.add(a)
        else:
            lista_male.add(a)

    for a in popular_list:
        if a in lista:
            outputPopular += '\n[[%s]]' % a

    date = datetime.datetime.now() + datetime.timedelta(hours=2) #TODO summer time/winter time
    data1 = date.strftime("Ostatnia aktualizacja: %Y-%m-%d, %H:%M:%S")

    final = final + data1
    final += '\n= najczęściej odwiedzane ='
    final += outputPopular
    final = final + '\n= wielka litera ='

    for b in lista_wielkie:
        final = final + '\n[[%s]]' % b

    final = final + '\n= mała litera ='

    for c in lista_male:
        final = final +  '\n[[%s]]' % c

    final_gw = data1 + '\n= gwary ='

    for d in outputGwary:
        final_gw = final_gw +  '\n[[%s]]' % d

    final_gw += '\n= przestarzałe ='

    for d in outputArchaic:
        final_gw += '\n[[%s]]' % d

    final = final + '\n= wyraz obcy w języku polskim ='

    for e in outputObce:
        final = final +  '\n[[%s]]' % e

    final = final + '\n= nieznalezione IPA='

    for f in lista_ipa:
        final = final +  '\n[[%s]]' % f


    final = final + '\n: Licznik istniejących: %d' % count_jest

    output_main.put(final, comment = 'Aktualizacja listy', botflag=False)
    if (len(output_gwary.get()) != len(final_gw)):
        output_gwary.put(final_gw, comment = 'Aktualizacja listy')


    re_po = re.compile('zmiana procentowa\n\|-(.*)', re.DOTALL)
    s_po = re.search(re_po, output_stat.get())
    re_proc = re.compile('zmiana procentowa\n\|-\n\|.*?\n\|.*?\n\| (.*?)\n')
    s_proc = re.search(re_proc, output_stat.get())
    proc_old = float(s_proc.group(1))
    proc = round(count_jest*100.00/count_all, 1)
    stat = '{| class="wikitable" style="text-align: center;"\n|-\n! data\n! istniejące\n! % istniejących\n! zmiana procentowa\n|-'
    stat = stat + '\n| %s\n| %d\n| %.1f\n| ' % ((datetime.datetime.now()-datetime.timedelta(days=1)).strftime("%Y-%m-%d"), count_jest, proc)
    if (proc-proc_old) < 0:
        stat = stat + 'style="background: #FF927D;" | '
    elif (proc-proc_old) > 0:
        stat = stat + 'style="background: #00E070;" | +'
    stat = stat + '%.1f\n|-' % (proc-proc_old)
    stat = stat + s_po.group(1)

    if (proc-proc_old != 0):
        output_stat.put(stat, comment = 'Aktualizacja tabeli')

    for a in lista_male:
        if re.search(re_r, a) == None:
            r = r + '\n[[%s]]' % a
        else:
            with_r.add('%s' % a)

    #print r
    output_r.put(r, comment = 'Aktualizacja listy słów bez litery r')

    with open('%s/public_html/pron_with_r.html' % (os.environ['HOME']), encoding='utf-8', mode='w') as f:
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n<html xmlns="http://www.w3.org/1999/xhtml\nxml:lang="pl">\n<head>\n<meta http-equiv="content-type" content="text/html; charset=UTF-8" />\n</head><body>')
        f.write('<br />' + data1 + '\n')
        
        for item in with_r:
            f.write('<br />' + item + '\n')
        
        f.write('</body></html>')

if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
