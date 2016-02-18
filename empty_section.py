# -*- coding: utf-8 -*-

from klasa import *
import re

def empty_section(section):

    re_numbers = re.compile(r'\: \(([0-9]\.[0-9])\)\s*(.*)')

    empty_content = ['']
    if section == 'przykłady':
        empty_content += ['\n: (1.1)', '\n: (1.1) ']

    excluded_pos = ['rzeczownik', '{{forma']


    wordlist = getListFromXML('xx', findLatest=True)

    with open('output/empty_sectionsxx.txt', 'w') as f:
        for word in wordlist:
            try: h = Haslo(word)
            except sectionsNotFound:
                pass
            except WrongHeader:
                pass
            else:
                if h.type == 3:
                    for lang_section in h.listLangs:
                        if lang_section.lang == 'polski':
                            lang_section.pola()
                            if any(lang_section.subSections['przykłady'].text == empty for empty in empty_content) \
                               and not any(pos in lang_section.subSections['znaczenia'].text for pos in excluded_pos):
                               
                                defs_found = re.findall(re_numbers, lang_section.subSections['znaczenia'].text)
                                for defn in defs_found:
                                    if 'dokonany od' not in defn[1] or '{{zob' not in defn[1]:
                                        f.write(h.title + '\n')
                                        break
