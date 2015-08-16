#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import Category
from pywikibot import pagegenerators
import re
from klasa import *
from importsjp import *

def addAspekt(title):
    # regex fetching all the data needed for the creation of new pages
    re_aspekt = re.compile(r'\'\'czasownik (nie|)przechodni (nie|)dokonany\'\'\s*\(\{\{(n|)dk\}\}( .*?)\)')
    word = Haslo(title)

    przech = None # transitive/intransitive
    dk = None # dk = perfective
    ndk = None # ndk = imperfective

    if word.type == 3:
        for sekcja in word.listLangs:
            if sekcja.lang == 'polski':
                sekcja.pola()
                if sekcja.type != 7: # type 7 means that although 'polski' should be the language, the section structure does not match
                    for mean in sekcja.znaczeniaDetail:
                        if 'aspekt dokonany' in mean[1] or 'aspekt niedokonany' in mean[1] or '{{dokonany od' in mean[1] or '{{niedokonany od' in mean[1] or '{{zob' in mean[1]:
                            return 0

                        # both templates below shouldn't occur at the same time in the part of speech description
                        if '{{ndk}}' in mean[0] and '{{dk}}' in mean[0]:
                            log('*[[%s]] - {{dk}} i {{ndk}} w opisie części mowy' % (title), 'aspekty')
                            return 0

                    if '{{zobtłum aspekt' in sekcja.tlumaczenia.text:
                        log('*[[%s]] - możliwe podwójne przekierowanie' % (title), 'aspekty')
                        return 0

                    for mean in sekcja.znaczeniaDetail:
                        s_aspekt = re.search(re_aspekt, mean[0])

                        if s_aspekt:
                            newTitle = ''
                            przech = s_aspekt.group(1) # transitive or intransitive
                            ndk_or_dk = s_aspekt.group(2) # perfective or imperfective
                            opp_ndk_or_dk = s_aspekt.group(3) # new aspect (at the end of the line, in parentheses) - perfective or imperfective
                            opp = s_aspekt.group(4) # new aspect - page title
                            print(opp)
                            # if the first is perfective and the one in parentheses is also perfective, then sth is wrong (the same for imperfective)
                            if (ndk_or_dk == 'nie' and opp_ndk_or_dk == 'n') or (ndk_or_dk == opp_ndk_or_dk):
                                log('*[[%s]] - w opisie dwa razy ndk albo dk' % (title), 'aspekty')
                                continue

                            # searching for strange things in the POS description
                            if '\'\'\'' in opp or ('\'\'' not in opp and '[[' not in opp):
                                log('*[[%s]] - dziwny opis części mowy' % (title), 'aspekty')
                                continue

                            # if there are a few corresponding aspects, we need a list
                            opp_list = opp.split('/')
                            for i,v in enumerate(opp_list):
                                opp_list[i] = opp_list[i].strip().strip('[').strip(']')

                            # if there is no corresponding aspect, skip this iteration
                            if opp_list[0] == '\'\'brak\'\'':
                                continue

                            # strings for new POS description
                            if ndk_or_dk == 'nie':
                                ndkNew = ''
                                ndkShort = 'n'
                            else:
                                ndkNew = 'nie'
                                ndkShort = ''

                            # for each element in corresponding aspect list, create a new page
                            for newTitle in opp_list:
                                nowe = Haslo(title=newTitle)
                                if nowe.type == 0:
                                    log('*[[%s]] - redirect' % (newTitle), 'aspekty')
                                elif nowe.type == 1 and ' ' not in newTitle and ',' not in newTitle and '/' not in newTitle:
                                    nowe = Haslo(title=newTitle, new=True)
                                    nowaSekcja = Sekcja(title=newTitle, type=9, lang='język polski')
                                    nowaSekcja.znaczeniaDetail.append(['\'\'czasownik %sprzechodni %sdokonany\'\' ({{%sdk}} [[%s]])' % (przech, ndkNew, ndkShort, title), '\n: (1.1) {{%sdokonany od|%s}}' % (ndkNew, title)])
                                    nowaSekcja.tlumaczenia.text = '\n: (1.1) {{zobtłum aspekt|%s}}' % title

                                    tempWord = HasloSJP(newTitle) # fetching flex tables from sjp.pl
                                    if len(tempWord.words) == 1:
                                        tempWord.words[0].flexTable(odmOlafa)
                                        wt = tempWord.words[0].wikitable
                                        nowaSekcja.odmiana.text = '\n: (1.1) %s' % wt
                                    nowaSekcja.saveChanges()
                                    nowe.addSection(nowaSekcja)
                                    page = pywikibot.Page(site, newTitle)

                                    try: content = page.get()
                                    except pywikibot.NoPage:
                                        nowe.push(False, 'dodanie hasła o aspekcie na podstawie [[%s]]' % (title), True)

def main():
    global odmOlafa
    odmOlafa = OdmianaOlafa()
    global site
    site = pywikibot.getSite()
    templatePageNdk = pywikibot.Page(site, 'Szablon:ndk')
    lista_ndk = pagegenerators.ReferringPageGenerator(templatePageNdk, True, True, True)
    templatePageDk = pywikibot.Page(site, 'Szablon:dk')
    lista_dk = pagegenerators.ReferringPageGenerator(templatePageDk, True, True, True)
    lista = set(list(lista_ndk)+list(lista_dk))
    #lista = [pywikibot.Page(site, u'spróbować')]
    for a in lista:
        addAspekt(a.title())

if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
