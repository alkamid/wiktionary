#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators
import re
from pywikibot import xmlreader
import collections
from klasa import *
import config

# the script looks for newly added languages (the languages for which the templates do not exist)
def missingLangs(data):

    data_slownie = data[6] + data[7] + '.' + data[4] + data[5] + '.' + data[0] + data[1] + data[2] + data[3]
    lista_stron = getListFromXML(data)
    wikt = pywikibot.Site('pl', 'wiktionary')
    foundList = set()
    notFound = set()

    LangsMediaWiki = getAllLanguages()

    for a in lista_stron:

        try: word = Haslo(a)
        except notFromMainNamespace:
            pass
        except sectionsNotFound:
            pass
        except WrongHeader:
            pass
        else:
            if word.type == 3:
                for lang in word.listLangs:
                    if lang.type != 2:
                        if lang.lang not in foundList:
                            foundList.add(lang.lang)

    existing = set(a.shortName for a in LangsMediaWiki)
    diff = foundList - existing

    missingText = ''

    with open('%soutput/missingLangs.txt' % (config.path['scripts']), encoding='utf-8', mode='w') as f:
        for a in lista_stron:
            try: word = Haslo(a)
            except notFromMainNamespace:
                pass
            except sectionsNotFound:
                pass
            except WrongHeader:
                pass
            else:
                if word.type == 3:
                    for lang in word.listLangs:
                        if lang.type != 2:
                            if lang.lang in diff:
                                f.write('%s - %s\n' % (lang.lang, word.title))
