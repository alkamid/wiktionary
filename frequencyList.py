#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
from pywikibot import Category
import pywikibot
from pywikibot import pagegenerators
import re
from pywikibot import xmlreader
from klasa import *
import config


# the list of words that are ignored in all frequency lists
def getDeletedList():
    deleted = set()
    site = pywikibot.Site()
    pageDeleted = pywikibot.Page(site, u'Wikisłownik:Ranking brakujących tłumaczeń/zawsze usuwane')
    for line in pageDeleted.get().split('\n'):
        if line[0] == ':':
            lineList = line.split('[[')
            deleted.add(lineList[1].strip(']'))
    return deleted

def frequencyList(data):
    
    site = pywikibot.Site()
    lista_stron2 = getListFromXML(data)
    ranking = {}
    re_example_translation = re.compile(u'→(.*?)(?=\<ref|\n|$)')
    re_colloc_translation = re.compile(u'→(.*?)(?=\<ref|\n|•|;|$)')
    re_link = re.compile(u'\[\[([^\:]*?)(?=\]\]|\||#pl)')
    alltitles = set()

    deleted = getDeletedList()

    i = 1
    for a in lista_stron2:            
        alltitles.add(a.title)
        if 'Wikipedysta:AlkamidBot' not in a.title:
            try: h = Haslo(a)
            except sectionsNotFound:
                pass
            except WrongHeader:
                pass
            else:
                if h.type == 3:    
                    to_search = ''
                    for sekcja in h.listLangs:
                        sekcja.pola()
                        if sekcja.type not in (2,4,5,7,11):
                            if sekcja.lang == 'polski' or sekcja.lang == u'termin obcy w języku polskim':
                                for elem in (u'dodatki', u'znaczenia', u'przykłady', u'składnia', u'kolokacje', u'synonimy', u'antonimy', u'pokrewne', u'frazeologia', u'etymologia', u'uwagi'):
                                    to_search += sekcja.subSections[elem].text
                    
                            else:
                                s_example_translation = None
                                s_colloc_translation = None
                                
                                if u'→' in sekcja.subSections[u'przykłady'].text:
                                    s_example_translation = re.findall(re_example_translation, sekcja.subSections[u'przykłady'].text)
                                if s_example_translation:
                                    for a in s_example_translation:
                                        to_search += a
                                if u'→' in sekcja.subSections[u'kolokacje'].text:
                                    s_colloc_translation = re.findall(re_colloc_translation, sekcja.subSections['kolokacje'].text)
                                if s_colloc_translation:
                                    for a in s_colloc_translation:
                                        to_search += a
                                        
                                to_search = to_search + sekcja.subSections['znaczenia'].text
                    
                    s_link = re.findall(re_link, to_search)     
                    for link in s_link:
                        if '#' not in link and link not in deleted: #if there is a hash in the link, it is not '#pl' (excluded in regex), therefore not a Polish link; also, exlude words from deleted list
                            try: ranking[link]
                            except KeyError:
                                ranking[link] = 1
                            else:
                                ranking[link] += 1
               

    dictlist = []
    for key, value in ranking.iteritems():
        temp = [key,value]
        dictlist.append(temp)
    
    def sortkey(row):
       return float(row[1])
        
    dictlist.sort(key=sortkey, reverse=True)
    
    htmllist = u'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n<html xmlns="http://www.w3.org/1999/xhtml\nxml:lang="pl">\n<head>\n<meta http-equiv="content-type" content="text/html; charset=UTF-8" />\n</head><body>'
    
    alltext = []

    for i in range(5):
        alltext.append('')

    i = 0
    for elem in dictlist:
        if i>20000:
            break
        htmllist += u'\n%s=%d' % (elem[0], elem[1])
        if i<10000:
            alltext[i/2000] += u'\n[[%s]]=%d' % (elem[0], elem[1])
        i+= 1
       
    dictlist = [s for s in dictlist if s[0] not in alltitles]
    
    nonExistingText = ''
    for elem in dictlist:
        nonExistingText += u'\n%s=%d' % (elem[0], elem[1])
        
    nonExistingText = nonExistingText.strip()
     
    for num, elem in enumerate(alltext):
        elem = elem.strip()
        outputPage = pywikibot.Page(site, u'Indeks:Polski - Najpopularniejsze słowa %d-%d' % (num*2000+1, (num+1)*2000))
        elem = u'Lista frekwencyjna języka polskiego na podstawie odnośników na stronach Wikisłownika.\n\n{{język linków|polski}}\n' + elem + u'\n[[Kategoria:Polski (słowniki tematyczne)]]\n[[Kategoria:Listy frekwencyjne|polski]]'
        outputPage.save(elem, comment='aktualizacja')
    
    htmllist += u'</body></html>'
    file = open('%spublic_html/frequencyListPL.html' % (config.path['home']), 'w')
    file.write(htmllist.encode( "utf-8" ))
    file.close
    
    file = open('%soutput/frequencyListPL.txt' % (config.path['scripts']), 'w')
    file.write(nonExistingText.encode( "utf-8" ))
    file.close
    

#if __name__ == "__main__":
#    frequencyList('20141024')
