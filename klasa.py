#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot
import re
import codecs
import collections
import locale
import time
import datetime
import os
#import config
from pywikibot import xmlreader
import bz2
import sys
from pywikibot.data.api import Request
from os import environ
#import mwparserfromhell
from copy import deepcopy
from difflib import SequenceMatcher

'''experimental: think about using mwparserfromhell
def parseTitle(title):
    site = pywikibot.Site()
    page = pywikibot.Page(site, title)
    text = page.get()
    return mwparserfromhell.parse(text)

def parseText(text):
    return mwparserfromhell.parse(text)
'''
locale.setlocale(locale.LC_COLLATE,"pl_PL.UTF-8")
#possible types:
#0 - redirect
#1 - page does not exist
#2 - pywikibot.error
#3 - valid page
#4 - page exists, but no language sections were found
#5 - not from the main namespace

class Haslo():
    regex = {}
    regex['langs-wstepna'] = re.compile(r'(.*?)==', re.DOTALL)
    regex['langs-lang'] = re.compile(r'(== .*?\(\{\{.*?\}\}\) ==.*?)(?=$|[^{{]==)', re.DOTALL)
    def __init__(self, title, text='faoweoucmo3u4210987acskjdh', new=False):
        if new == True:
            self.site = pywikibot.Site('pl', 'wiktionary')
            self.type = 3
            self.title = title
            self.wstepna = ''
            self.content = ''
            self.listLangs = []

        elif type(title) is str:
            self.site = pywikibot.Site('pl', 'wiktionary')
            self.type = 1
            self.title = title
            self.wstepna = ''
            page = pywikibot.Page(self.site, self.title)

            try:
                self.content = page.get()
            except pywikibot.IsRedirectPage:
                self.type = 0
            except pywikibot.NoPage:
                self.type = 1
            except pywikibot.Error:
                self.type = 2
            else:
                self.type = 3
                if int(page.namespace()) != 0 and 'Wikipedysta:AlkamidBot/sjp/' not in self.title:
                    self.type = 5

                if self.type == 3:
                    self.langs()

        else:
            self.title = title.title
            self.content = title.text
            self.type = 3
            #checking the namespace
            if title.ns != '0':
                self.type = 5

            if self.type == 3:
                self.langs()

    def langs(self):
        self.listLangs = []
        s_wstepna = re.search(Haslo.regex['langs-wstepna'], self.content)
        if s_wstepna:
            self.wstepna = s_wstepna.group(1)
        else:
            self.wstepna = ''

        s_lang = re.findall(Haslo.regex['langs-lang'], self.content)
        if s_lang:
            for b in s_lang:
                self.listLangs.append(LanguageSection(b, self.title))
        else:
            self.type = 4
            raise sectionsNotFound

    def push(self, offline=False, myComment = '', new=False):

        toPush = self.wstepna
        sthWrong = 0
        if not ':' in self.title:
            self.listLangs = sortSections(self.listLangs)
        for a in self.listLangs:
            if a.type in (2,3,7):
                sthWrong = 1
            toPush += a.header + '\n' + a.content.strip() + '\n\n'
        toPush = toPush.strip()
        if not sthWrong:
            if offline:
                print(toPush)
            else:
                page = pywikibot.Page(self.site, self.title)
                try: content = page.get()
                except pywikibot.IsRedirectPage:
                    print('%s - konflikt edycji' % self.title)
                except pywikibot.NoPage:
                    if new:
                        page.text = toPush
                        page.save(comment=myComment)
                except pywikibot.Error:
                    print('%s - konflikt edycji' % self.title)
                else:
                    if content == self.content and content != toPush:
                        page.text = toPush
                        page.save(comment=myComment)
                    elif content != self.content:
                        print('%s - konflikt edycji' % self.title)
    def addSection(self, section):
        self.listLangs.append(section)

def sortSections(sectionList):
    """ sorting sections. The proper order is:
    1. "użycie międzynarodowe"
    2. "polski"
    3. "termin obcy w języku polskim"
    4. "znak chiński"
    The rest is sorted alphabetically with pl_PL locale
    
    @param sectionList: a list of language sections to be sorted
    @type sectionList: list of LanguageSection() objects
    
    """
    
    sectionList = sorted(sectionList, key=lambda x: locale.strxfrm(x.lang))
    
    for lang in ['znak chiński', 'termin obcy w języku polskim', 'polski', 'użycie międzynarodowe']:
        for sec in sectionList:
            if sec.lang == lang:
                ind = sectionList.index(sec)
                sectionList.insert(0, sectionList.pop(ind))

    return sectionList

class notFromMainNamespace(Exception):
    def __init__(self):
        self.value = 'not from main namespace!'
    def __str__(self):
        return repr(self.value)

class sectionsNotFound(Exception):
    def __init__(self):
        self.value = 'language sections not found!'
    def __str__(self):
        return repr(self.value)

class DumpNotFound(Exception):
    def __init__(self):
        self.value = 'the latest dump has not been found'
    def __str__(self):
        return repr(self.value)

class WrongHeader(Exception):
    def __init__(self):
        self.value = 'something is wrong with the header'
    def __str__(self):
        return repr(self.value)

class NotExampleField(Exception):
    def __init__(self):
        self.value = 'this method only works for {{przykłady}} subsection'
    def __str__(self):
        return repr(self.value)


def generateRegexp(order):
    for i, sect in enumerate(order):
        if i == len(order) - 1:
            order[i].regex = re.compile(r'%s(.*)' % (order[i].template), re.DOTALL)
        else:
            order[i].regex = re.compile(r'%s(.*?)\n%s' % (order[i].template, order[i+1].template), re.DOTALL)

#possible types:
#1 - proper section, all normal languages
#2 - can't find a language in the header
#4 - chinese sign (znak chiński)
#5 - can't find separate meanings
#6 - japanese
#7 - the parser cannot assign the section to any language
#8 - korean kanji
#9 - polish word
#10 - esperanto morpheme
#12 - esperanto
#13 - ancient egyptian
#14 - numbering of meanings is wrong
#TODO: numerek dla każdego z typów

class subSection():
    def __init__(self, template, optional=False, name=None, regex=None):
        if name:
            self.name = name
        else:
            self.name = template
        if template != '':
            self.template = '{{%s}}' % template
        else:
            self.template = ''
        self.optional = optional
        self.regex = regex

class LanguageSection():
    regex = {}
    regex['init-lang'] = re.compile(r'== (.*?) \(\{\{(język |)(.*?)(?=\|(.*?)\}\}\) ==|\}\}\) ==)')
    regex['init-langLong'] = re.compile(r'== (.*?) \(\{\{(.*?)(\|.*?\}\}\) ==|\}\}\) ==)')
    regex['init-headerAndContent'] = re.compile(r'\s*(== .*? \({{.*?}}\) ==)[ ]*\n(.*)', re.DOTALL)

    regex['pola-znaczeniaDetail'] = re.compile(r'\n\s*?(\'\'.*?|{{forma rzeczownika.*?|{{forma przymiotnika.*?|{{forma czasownika.*?|{{przysłowie .*?|{{morfem\|.*?)\s*?(\n\s*?\: \([0-9]\.[0-9]\.*[0-9]*\).*?)(?=\n\'\'|\n{{forma rzeczownika|\n{{forma przymiotnika|\n{{forma czasownika|\n{{przysłowie|\n{{morfem\||$)', re.DOTALL)

    regex['pola-nr'] = re.compile(r'\(([0-9]\.[0-9]\.*[0-9]*)\)')

    # define subsection order for different languages. Could be fetched from pl.wikt if we had it written somewhere

    sectionOrder = collections.OrderedDict() # we want to keep subsections ordered

    # first, standard subsections template. The rest is adding/subtracting specific subsections for a few languages
    sectionOrder['default'] = [subSection('', True, name='dodatki'),
                               subSection('wymowa'), subSection('znaczenia'),
                               subSection('odmiana'), subSection('przykłady'),
                               subSection('składnia'), subSection('kolokacje'),
                               subSection('synonimy'), subSection('antonimy'),
                               subSection('hiperonimy', optional=True),
                               subSection('hiponimy', optional=True),
                               subSection('holonimy', optional=True),
                               subSection('meronimy', optional=True),
                               subSection('pokrewne'), subSection('frazeologia'),
                               subSection('etymologia'), subSection('uwagi'),
                               subSection('źródła')]

    sectionOrder['znak chiński'] = [subSection('klucz'), subSection('kreski'),
                                    subSection('warianty'), subSection('kolejność'),
                                    subSection('znaczenia'), subSection('etymologia'),
                                    subSection('kody'), subSection('słowniki'), subSection('uwagi')]

    sectionOrder['staroegipski'] = [subSection('', True, name='dodatki'),
                                    subSection('zapis hieroglificzny'),
                                    subSection('transliteracja'), subSection('transkrypcja'),
                                    subSection('znaczenia'), subSection('determinatywy')] + deepcopy(sectionOrder['default'])
    del sectionOrder['staroegipski'][6:9]

    sectionOrder['polski'] = deepcopy(sectionOrder['default'])
    sectionOrder['polski'].insert(-1, subSection('tłumaczenia'))

    sectionOrder['esperanto (morfem)'] = deepcopy(sectionOrder['default'])
    sectionOrder['esperanto (morfem)'].insert(9, subSection('pochodne'))
    del sectionOrder['esperanto (morfem)'][10:15]

    sectionOrder['esperanto'] = deepcopy(sectionOrder['default'])
    sectionOrder['esperanto'].insert(1, subSection('morfologia'))

    sectionOrder['japoński'] = deepcopy(sectionOrder['default'])
    sectionOrder['japoński'].insert(1, subSection('czytania'))
    sectionOrder['japoński'].insert(14, subSection('złożenia'))

    sectionOrder['koreański'] = deepcopy(sectionOrder['default'])
    sectionOrder['koreański'].insert(16, subSection('hanja'))



    # generate regexp for each template - we will use them for parsing every LanguageSection
    for order in sectionOrder:
        generateRegexp(sectionOrder[order])


    def __init__(self, text='afeof5imad3sfa5', title = '2o3iremdas', type=666, lang='bumbum'):

        self.subSections = collections.OrderedDict()
        self.inflectedOnly = False # denotes entries with inflected words only
        if text == 'afeof5imad3sfa5' and title != '2o3iremdas' and type != 666 and lang != 'bumbum':
            self.title = title
            self.langLong = lang
            self.lang = lang.replace('język ', '')
            self.type = type
            self.header = '== %s ({{%s}}) ==' % (title, lang)
            self.znaczeniaDetail = []
            if type == 1:
                try: order = LanguageSection.sectionOrder[self.lang]
                except KeyError:
                    order = LanguageSection.sectionOrder['default']
                for elem in order:
                    self.subSections[order[elem]] = Pole('')

        elif text != 'afeof5imad3sfa5' and type == 666 and lang == 'bumbum':

            s_lang = re.search(LanguageSection.regex['init-lang'], text)
            s_langLong = re.search(LanguageSection.regex['init-langLong'], text)
            s_headerAndContent = re.search(LanguageSection.regex['init-headerAndContent'], text)
            if s_lang and s_langLong and s_headerAndContent:
                self.title = title
                self.titleHeader = s_lang.group(1)
                if s_lang.group(4):
                    self.headerArg = s_lang.group(4)
                else:
                    self.headerArg = ''
                self.header = s_headerAndContent.group(1).strip()
                self.lang = s_lang.group(3)
                if len(self.lang) == 0:
                    self.type = 2
                    raise WrongHeader
                self.langUpper = self.lang[0].upper() + self.lang[1:]
                self.langLong = s_langLong.group(2)
                self.content = s_headerAndContent.group(2)
                self.type = 1
            else:
                self.type = 2
                raise WrongHeader

    def updateHeader(self):

        self.header = '== %s ({{%s' % (self.titleHeader, self.langLong)
        if self.headerArg:
            self.header += '|%s' % self.headerArg
        self.header += '}}) =='

    def saveChanges(self):
        try: self.subSections['znaczenia']
        except AttributeError:
            pass
        else:
            znaczeniaWhole = ''
            for a in self.znaczeniaDetail: # łączy sekcję "znaczenia" (jest wcześniej rozbijana na "część mowy" i znaczenie)
                znaczeniaWhole += '\n' + a[0] + a[1]
            self.subSections['znaczenia'] = Pole(znaczeniaWhole)


        self.content = ''
        for elem in self.subSections:
            if elem == 'dodatki':
                self.content += self.subSections[elem].text
            else:
                self.content += '\n{{%s}}%s' % (elem, self.subSections[elem].text)

    def pola(self):

        if self.type == 1:
            try: order = LanguageSection.sectionOrder[self.lang] # look for subsection order templates for specific languages
            except KeyError:
                order = LanguageSection.sectionOrder['default']
            for sect in order:
                s = re.search(sect.regex, self.content)
                if s:
                    self.subSections[sect.name] = Pole(s.group(1))
                elif sect.optional:
                    self.subSections[sect.name] = Pole('')
                else:
                    self.type = 7
                    return 7


            s_znaczeniaDetail = re.findall(LanguageSection.regex['pola-znaczeniaDetail'], self.subSections['znaczenia'].text)
            if s_znaczeniaDetail:
                self.znaczeniaDetail = [list(tup) for tup in s_znaczeniaDetail]

                self.checkForInflectedForms(self.znaczeniaDetail)
                # checking if the last number [(1.1), (2.1) etc.] matches the length of self.znaczeniaDetail - if it doesn't, it means that the numbering is invalid
                s_numer = re.search(LanguageSection.regex['pola-nr'], self.znaczeniaDetail[-1][1])
                if int(s_numer.group(1)[0]) != len(self.znaczeniaDetail):
                    self.type = 14
            else:
                if self.lang == 'znak chiński':
                    self.znaczeniaDetail = []
                else:
                    self.type = 5

    def checkForInflectedForms(self, meanings):
        allFlexForms = True

        forms = set('forma ' + affix for affix in ('czasownika', 'liczebnika', 'przymiotnika', 'przysłówka', 'rodzajnika', 'rzeczownika', 'verbal', 'zaimka'))
        for mean in meanings:
            if any(form in mean[0] for form in forms):
                pass
            else:
                return False

        self.inflectedOnly = True

class Pole():
    regex = {}
    regex['init-warianty-details'] = re.compile(r'{{zch-w\|([a-z]*?)\|(.*?)}}')
    regex['init-obrazek'] = re.compile(r'{{zch-obrazek\|([a-z]*?)\|(.*?)}}')
    regex['init-kodySlowniki-details'] = re.compile(r'([a-z]*?)=(.*?)(?=\||$)')
    regex['init-kolejnosc'] = re.compile(r'({{zch-komiks|{{zch-animacja|{{zch-cienie)[\|]*(.*?)}}')
    regex['numer-nr-whole'] = re.compile(r'(\:\s*?\([1-9].*?\))(.*?)(?=\n\:|$)', re.DOTALL)

    def __init__(self, text, type='auto'):

        self.type = type
        self.text = text
        self.list = []
        self.dict = {}
        if type == 'warianty':
            warianty = re.findall(Pole.regex['init-warianty-details'], self.text)
            for b in warianty:
                if b[0] not in self.dict:
                    self.dict[b[0]] = []
                self.dict[b[0]].append(b[1])
            warianty_obrazek = re.findall(Pole.regex['init-obrazek'], self.text)
            for b in warianty_obrazek:
                self.dict[b[0]] = b[1]
        if type == 'zch-etym':
            etymologia = re.findall(Pole.regex['init-obrazek'], self.text)
            for b in etymologia:
                self.dict[b[0]] = b[1]
        if type == 'kolejnosc':
            kolejnosc = re.findall(Pole.regex['init-kolejnosc'], self.text)
            for b in kolejnosc:
                self.dict[b[1]] = b[0]
        if type == 'kody' or type == 'slowniki':
            kody = re.findall(Pole.regex['init-kodySlowniki-details'], self.text)
            for b in kody:
                self.dict[b[0]] = b[1]

    def add_example(self, num, example_text):
        #TODO: make it universal so it works for any subsection
        if self.type != 'auto':
            raise NotExampleField

        #https://regex101.com/r/xP6eR5/4
        #find all existing examples
        re_example = re.compile(r'(\: \(([0-9]\.[0-9]{1,2})\)\s{0,1}.*?)(?=\n\: \([0-9]\.[0-9]{1,2}\)|$)', re.DOTALL)
        s_examples = re.findall(re_example, self.text)

        re_refs = re.compile(r'(<ref.*?(?:/>|</ref>))')
        newtext_without_refs = re.sub(re_refs, '', example_text)
        newtext_without_quotes = newtext_without_refs.replace('\'\'', '')

        already_there = 0
        for e in s_examples:
            preprocessed = re.sub(re_refs, '', e[0])
            preprocessed = preprocessed.replace('\'\'', '')
            if SequenceMatcher(None, dewikify(preprocessed[8:]), dewikify(newtext_without_quotes)).ratio() > 0.8:
                already_there = 1
                break
        
        if already_there:
            return -1

        #add the given example
        s_examples.append((': ({0}) {1}'.format(num, example_text), str(num)))
        
        #sort examples
        sorted_examples = sorted(s_examples, key=lambda tup: tup[1])

        #join them as a string, excluding empty examples ": (1.1) "
        self.text = '\n' + '\n'.join([a[0] for a in sorted_examples if len(a[0]) > 8])
        return 1


    def merge(self, mode=2): #mode = 1 - test for a proper field, return 0 if invalid; mode=2 - merge a list/dict into a string
        text=''
        if self.type == 'warianty':
            #TODO: this code can be shortened with two for loops
            text = ' |'
            if 'ct' in self.dict:
                for a in self.dict['ct']:
                    text += ' {{zch-w|ct|%s}} |' % a
            if 'cu' in self.dict:
                for a in self.dict['cu']:
                    text += ' {{zch-w|cu|%s}} |' % a
            if 'js' in self.dict:
                for a in self.dict['js']:
                    text += ' {{zch-w|js|%s}} |' % a
            if text[-2:] == ' |':
                text = text[:-2]
            if text == '':
                text += '|{{zch-w}}'
            if 'c' in self.dict or 'xt' in self.dict or 'ca' in self.dict or 'kt' in self.dict or 'sot' in self.dict:
                text += '}} {{warianty-obrazek |'
            if 'c' in self.dict:
                text += ' {{zch-obrazek|c|%s}} |' % self.dict['c']
            if 'xt' in self.dict:
                text += ' {{zch-obrazek|xt|%s}} |' % self.dict['xt']
            if 'ca' in self.dict:
                text += ' {{zch-obrazek|ca|%s}} |' % self.dict['ca']
            if 'kt' in self.dict:
                text += ' {{zch-obrazek|kt|%s}} |' % self.dict['kt']
            if 'sot' in self.dict:
                text += ' {{zch-obrazek|sot|%s}} |' % self.dict['sot']
            if text[-2:] == ' |':
                text = text[:-2]
        if self.type == 'zch-etym':
            if 'o' in self.dict or 'br' in self.dict or 'bs' in self.dict or 'ss' in self.dict:
                text += ' {{warianty-obrazek |'
            if 'o' in self.dict:
                text += ' {{zch-obrazek|o|%s}} |' % self.dict['o']
            if 'br' in self.dict:
                text += ' {{zch-obrazek|br|%s}} |' % self.dict['br']
            if 'bs' in self.dict:
                text += ' {{zch-obrazek|bs|%s}} |' % self.dict['bs']
            if 'ss' in self.dict:
                text += ' {{zch-obrazek|ss|%s}} |' % self.dict['ss']
            if text[-2:] == ' |':
                text = text[:-2]
            if text:
                text += '}}'
        if self.type == 'kolejnosc':
            if '' in self.dict:
                text += '%s}}' % self.dict['']
            if 'j' in self.dict:
                text += ' %s|j}}' % self.dict['j']
            if 't' in self.dict:
                text += ' %s|t}}' % self.dict['t']
            if 'a' in self.dict:
                text += ' %s|a}}' % self.dict['a']
            text.strip()
            if text:
                text = '\n' + text
        if self.type == 'kody':
            if 'cjz' in self.dict:
                text += '|cjz=%s' % self.dict['cjz']
            if 'cr' in self.dict:
                text += '|cr=%s' % self.dict['cr']
            if 'u' in self.dict:
                text += '|u=%s' % self.dict['u']
        if self.type == 'slowniki':
            if 'kx' in self.dict:
                text += '|kx=%s' % self.dict['kx']
            if 'dkj' in self.dict:
                text += '|dkj=%s' % self.dict['dkj']
            if 'dj' in self.dict:
                text += '|dj=%s' % self.dict['dj']
            if 'hdz' in self.dict:
                text += '|hdz=%s' % self.dict['hdz']
        if mode == 1:
            if text != self.text:
                return 0
            else:
                return 1
        else:
            self.text = text
            return text
    def numer(self):
        s_nr_whole = re.findall(Pole.regex['numer-nr-whole'], self.text)
        testString = ''
        if s_nr_whole:
            self.list = [list(tup) for tup in s_nr_whole]
            for elem in self.list:
                for e in elem:
                    testString += e
            if testString.strip().replace('\n', '') != self.text.strip().replace('\n', ''):
                self.type = 3
            else:
                self.type = 2
        else:
            self.type = 1
def ReadList(filename):
    list = []
    inp = codecs.open('%s' % filename, encoding='utf-8')
    for line in inp:
        list.append(line.split('\n'))
    return list

def flagLastRev(site, revid, comment=''):

    token = site.getToken(sysop=False)
    params = {
            'site': site,
        'action': 'review',
        'revid': revid,
        'token': token,
        'flag_accuracy': 1,
        'comment': comment,
    }

    req = Request(**params)
    query = req.submit()


#TODO: pobierać z WS:Kody języków
def getAllLanguages():
    site = pywikibot.Site('pl', 'wiktionary')
    page = pywikibot.Page(site, 'Mediawiki:Gadget-langdata.js')
    pageText = page.get()

    langTable = []
    shortOnly = []
    re_langs = re.compile(r'lang2code: \{\n(.*?)\n\t\},', re.DOTALL)
    re_oneLang = re.compile(r'\s*?\"(.*?)\"\s*?\:\s*\"([a-z-]*?)\"')
    re_shorts = re.compile(r'shortLangs: \[\n(.*?)\n\t\]', re.DOTALL)
    re_oneShort = re.compile(r'\s*?\"(.*?)\"(?:,\s*|\n)?')

    s_langs = re.search(re_langs, pageText)

    if s_langs:
        tempLangTable = re.findall(re_oneLang, s_langs.group(1))
        s_shorts = re.search(re_shorts, pageText)
        if s_shorts:
            shortOnly = re.findall(re_oneShort, s_shorts.group(1))
        for a in tempLangTable:
            if a[0] in shortOnly:
                tempLong = a[0]
            else:
                tempLong = 'język %s' % (a[0])

            langUpper = a[0][0].upper() + a[0][1:]

            langTable.append(Language(a[0], tempLong, langUpper, a[1]))
    else:
        print('Couldn\'t get languages list!')
        langTable = None

    return langTable

def obrazkiAndrzeja():
    #wyniki działania funkcji to dictionary w formie dict['slowo'] = [grafika1, grafika2, ...]
    site = pywikibot.Site()
    pageImages = pywikibot.Page(site, 'Wikipedysta:Andrzej 22/Ilustracje')
    re_sekcja = re.compile(r'\=\=\s*\[\[(.*?)\]\]\s*\=\=(.*?)(?=\=\=)', re.DOTALL)
    re_img = re.compile(r'(\[\[Plik\:.*?\]\])(?=\[\[Plik|<br)')
    re_subnr = ws = re.compile(r'\([0-9]\.[0-9]\)') # do zamieniania (1.1) na {{brak|numer}} w obrazkach
    pageText = pageImages.get()
    s_sekcja = re.findall(re_sekcja, pageText)
    result = collections.defaultdict()
    if s_sekcja:
        for a in s_sekcja:
            s_img = re.findall(re_img, a[1])
            if s_img and a[0]:
                result[a[0]] = []
                for b in s_img:
                    b = re.sub(re_subnr, '{{brak|numer}}', b)
                    result[a[0]].append(b)
    return result

class Language():
    def __init__(self, shortName, longName, langUpper, code):
        self.shortName = shortName
        self.longName = longName
        self.upperName = langUpper
        self.code = code

class SectionFr():
    def __init__(self, b, a):
        re_lang = re.compile('==(| )?{{=(.*?)=}}')
        s_lang = re.search(re_lang, b)
        if s_lang:
            self.title = a
            self.lang = s_lang.group(2)
            self.content = b
            self.type = 1
        else:
            self.type = 2

    def pola(self):
        if self.type == 1:
            re_etymology = re.compile('{{-étym-}}\n(.*?){{-|$', re.DOTALL)
            re_variants = re.compile('{{-var-ortho-}}\n(.*?){{-|$', re.DOTALL)
            re_synonyms = re.compile('{{-syn-}}\n(.*?){{-|$', re.DOTALL)
            re_antonyms = re.compile('{{-ant-}}\n(.*?){{-|$', re.DOTALL)
            re_derives = re.compile('{{-drv-}}\n(.*?){{-|$', re.DOTALL)
            re_expressions = re.compile('{{-exp-}}\n(.*?){{-|$', re.DOTALL)
            re_translations = re.compile('{{-trad-}}\n(.*?){{-|$', re.DOTALL)
            re_pronunciation = re.compile('{{-pron-}}\n(.*?){{-|$', re.DOTALL)
            re_noun = re.compile('{{-nom-\|(.*?){{-|$', re.DOTALL)

            s_etymology = re.search(re_etymology, self.content)
            s_variants = re.search(re_variants, self.content)
            s_synonyms = re.search(re_synonyms, self.content)
            s_antonyms = re.search(re_antonyms, self.content)
            s_derives = re.search(re_derives, self.content)
            s_expressions = re.search(re_expressions, self.content)
            s_translations = re.search(re_translations, self.content)
            s_pronunciation = re.search(re_pronunciation, self.content)
            s_noun = re.search(re_noun, self.content)


            if s_synonyms.group(1):
                self.synonyms = Pole(s_synonyms.group(1))
            else:
                self.synonyms = Pole(None)

            if s_etymology.group(1):
                self.etymology = Pole(s_etymology.group(1))
            else:
                self.etymology = Pole(None)

            if s_variants.group(1):
                self.variants = Pole(s_variants.group(1))
            else:
                self.variants = Pole(None)

            if s_antonyms.group(1):
                self.antonyms = Pole(s_antonyms.group(1))
            else:
                self.antonyms = Pole(None)

            if s_derives.group(1):
                self.derives = Pole(s_derives.group(1))
            else:
                self.derives = Pole(None)

            if s_expressions.group(1):
                self.expressions = Pole(s_expressions.group(1))
            else:
                self.expressions = Pole(None)

            if s_translations.group(1):
                self.translations = Pole(s_translations.group(1))
            else:
                self.translations = Pole(None)

            if s_pronunciation.group(1):
                self.pronunciation = Pole(s_pronunciation.group(1))
            else:
                self.pronunciation = Pole(None)

            if s_noun.group(1):
                self.noun = Pole(s_noun.group(1))
                self.genre()
            else:
                self.noun = Pole(None)

    def genre(self):

        if '{{m}}' in self.noun.tresc:
            self.genre = 'm'
        elif '{{f}}' in self.noun.tresc:
            self.genre = 'f'
        elif '{{mf}}' in self.noun.tresc:
            self.genre = 'mf'
        elif '{{mf?}}' in self.noun.tresc:
            self.genre = 'mf?'
        else:
            self.genre = 'unknown'

def pageCounter(language):
    #returns number of entries for a language
    params = {
                    'action'        :'expandtemplates',
                    'text'          :'{{PAGESINCAT:%s (indeks)|R}}' % language,
                    }
    req = Request(**params)
    qr = req.submit()
    print(qr['expandtemplates']['*'])

def RecentChanges(limit):
    limitString = limit
    time_format = "%Y-%m-%dT%H:%M:%SZ"
    limit = datetime.datetime.fromtimestamp(time.mktime(time.strptime(limitString, time_format)))
    current = datetime.datetime.now()
    list = set()
    params = {
            'action'    :'query',
            'list'          :'recentchanges',
                    'rcprop'        :'timestamp|title',
                    'rclimit'       :'100',
                    'rcnamespace': 0
            }

    while current > limit:
        textDate = current.strftime(time_format)
        params['rcstart'] = textDate
        req = Request(**params)
        qr = req.submit()
        try: current = datetime.datetime.fromtimestamp(time.mktime(time.strptime(qr['query-continue']['recentchanges']['rcstart'], time_format)))
        except KeyError:
            for elem in qr['query']['recentchanges']:
                list.add(elem['title'])
            break
        else:
            for elem in qr['query']['recentchanges']:
                list.add(elem['title'])
    return list


def writeRCLimit(name, limit=666):
    if limit == 666:
        time_format = "%Y-%m-%dT%H:%M:%SZ"
        current = datetime.datetime.now()
        limit = current.strftime(time_format)

    file = open('%srclimits/%s.txt' % (config.path['scripts'], name), 'w')
    file.write(limit)
    file.close
def readRCLimit(name):
    file = open('%srclimits/%s.txt' % (config.path['scripts'], name), 'r')
    data = file.readlines()
    return data[0].strip()
    file.close

def checkForNewDumps(lastUpdate):
    #lastUpdate is a date of the previous dump
    #returns new dump's date if found, if not returns 1

    year = int(lastUpdate[:4])
    month = int(lastUpdate[4:6])
    day = int(lastUpdate[6:8])

    lastDumpDate = datetime.datetime(year,month,day)
    now = datetime.datetime.now() #there is no point searching in the future, so limit the loops to today's date

    checked = lastDumpDate + datetime.timedelta(days=1)

    while checked <= now:
        tempDate = checked.strftime('%Y%m%d')
        filename = config.path['dumps'] + tempDate

        checked = checked + datetime.timedelta(days=1) #checking day by day
        if os.path.isdir(filename):
            return tempDate
    return 1

def getListFromXML(date, findLatest=False):
    #converts a wikimedia dump to a python generator of xml entries
    #if findLatest True, it will search for the newest dump in dumps folder

    filename = config.path['dumps'] + '{0}/plwiktionary-{0}-pages-articles.xml.bz2'.format(date)
    
    if findLatest:
        now = datetime.datetime.now()
        checked = now
        found = 0

        while checked > (now - datetime.timedelta(days=90)):

            tempDate = checked.strftime('%Y%m%d')
            tempFilename = config.path['dumps'] + '{0}/plwiktionary-{0}-pages-articles.xml.bz2'.format(tempDate)

            if os.path.isfile(tempFilename):
                found = 1
                break

            checked -= datetime.timedelta(days=1) #checking day by day
                
        if found:
            filename = tempFilename
    
    if os.path.isfile(filename):
        generator = xmlreader.XmlDump.parse(xmlreader.XmlDump(filename))
        return generator
    else:
        print(filename)
        raise DumpNotFound


def log(text, filename='log_all', test_mode=0):
    if test_mode == 1:
        print(text)
    else:
        if text != '':
            file = open("%slog/%s.txt" % (config.path['scripts'], filename), 'a')
            file.write (('\n' + text))
            file.close

class HasloFr():
    def __init__(self, a):
        site = pywikibot.Site('fr', 'wiktionary')

        self.type = 1
        self.title = a
        self.page = pywikibot.Page(site, self.title)

        try:
            self.content = self.page.get()
        except pywikibot.IsRedirectPage:
            self.type = 0
        except pywikibot.NoPage:
            self.type = 1
        except pywikibot.Error:
            self.type = 2
        else:
            self.type = 3

    def langs(self):
        self.list_lang = []
        re_lang = re.compile('(==\s*?{{=.*?=}}\s*?==\n.*?)$|==', re.DOTALL)
        s_lang = re.findall(re_lang, self.content)
        for b in s_lang:
            self.list_lang.append(SectionFr(b, self.title))

class HasloFrXML():
    def __init__(self, a):
        self.type = 1
        self.title = a
        self.page = pywikibot.Page(site, self.title)

        try:
            self.content = self.page.get()
        except pywikibot.IsRedirectPage:
            self.type = 0
        except pywikibot.NoPage:
            self.type = 1
        except pywikibot.Error:
            self.type = 2
        else:
            self.type = 3

    def langs(self):
        self.list_lang = []
        re_lang = re.compile('(==\s*?{{=.*?=}}\s*?==\n.*?)$|==', re.DOTALL)
        s_lang = re.findall(re_lang, self.content)
        for b in s_lang:
            self.list_lang.append(SectionFr(b, self.title))
        else:
            self.type = 4

def dewikify(input_text):
    """
    Dewikify a wikified string.

    Args:
        input_text (str): wikified text ([[word]]s [[be|are]] [[write|written]]
            [[like]] [[this]])
    Returns:
        str: unwikified text (words are written like this)
    """
    
    #https://regex101.com/r/yB0pZ6/1
    re_base_form = re.compile(r'(\[\[(?:[^\]\|]*?\||)(.*?)\]\])')
    dewikified = re.sub(re_base_form, r'\2', input_text)
    return dewikified

#this is taken from http://code.activestate.com/recipes/578163-retry-loop/ - useful for some of the scripts that fetch things from websites - we don't want intermittent errors to crash the script
class RetryError(Exception):
    pass

def retryloop(attempts, timeout):
    starttime = time.time()
    success = set()
    for i in range(attempts):
        success.add(True)
        yield success.clear
        if success:
            return
        if time.time() > starttime + timeout:
            break
    raise RetryError

"""
Usage:

for retry in retryloop(10, timeout=30):
    try:
        something
    except SomeException:
        retry()

for retry in retryloop(10, timeout=30):
    something
    if somecondition:
        retry()

"""
#retry feature - end
