#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot as pwb
from klasa import *
import config

# the script looks for newly added languages (the languages for which the templates do not exist)
def missingLangs(date):

    pageList = getListFromXML(date)
    wikt = pwb.Site('pl', 'wiktionary')

    LangsMediaWiki = getAllLanguages()
    existing = set(a.shortName for a in LangsMediaWiki)

    with open('{0}output/missingLangs.txt'.format(config.path['scripts']), encoding='utf-8', mode='w') as f:
        for a in pageList:

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
                            if lang.lang not in existing:
                                f.write('{0} - {1}\n'.format(lang.lang, word.title))
