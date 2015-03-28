#!/usr/bin/python
# -*- coding: utf-8 -*-

# statystyka długości haseł - pobiera ja z xml

import codecs
from pywikibot import Category
import pywikibot
from pywikibot import pagegenerators
import re
from pywikibot import xmlreader
import math
import collections
from klasa import *
import mwparserfromhell

def countRanks(langStats):

    fields = [u'countWords', u'countMeans', u'countLen', u'avgLen', u'percAudio', u'percGraph', u'percRef']

    for field in fields:
        tempList = []
        for a in langStats:
            if field == u'avgLen':
                if langStats[a].countWords > 10:
                    tempList.append([langStats[a].longName, getattr(langStats[a], field)])
            else:
                tempList.append([langStats[a].longName, getattr(langStats[a], field)])

        def sortkey(row):
            return float(row[1])

        tempList.sort(key=sortkey, reverse=True)

        i = 1
        for a in tempList:
            for b in langStats:
                if a[0] == langStats[b].longName:
                    langStats[b].rank[field] = i
                    i += 1


class LangStats():
    def __init__(self, longName, shortName):
        self.longName = longName
        self.shortName = shortName
        self.countWords = 0
        self.countMeans = 0
        self.countLen = 0
        self.countAudio = 0 # words with at least one audio file
        self.countGraph = 0 # words with at least one image
        self.countAudioAll = 0 # the number of audio files in each word
        self.countGraphAll = 0 # the number of images in each word
        self.countRef = 0
        self.avgLen = 0.0
        self.avgMean = 0.0
        self.percAudio = 0.0
        self.percGraph = 0.0
        self.percRef = 0.0
        self.rank = {u'countWords': 0, u'countMeans': 0, u'countLen': 0, u'avgLen': 0, u'percAudio': 0, u'percGraph': 0, u'percRef': 0}

    def addLength(self, length):
        self.countLen += length

    def addMeans(self, means):
        self.countMeans += means

    def addAudio(self):
        self.countAudio += 1.0

    def addGraph(self):
        self.countGraph += 1.0

    def addAudioAll(self, count):
        self.countAudioAll += count

    def addGraphAll(self, count):
        self.countGraphAll += count

    def addRef(self, ref):
        self.countRef += ref

    def addWord(self):
        self.countWords += 1

    def countAvgLen(self):
        if self.countWords:
            self.avgLen = self.countLen/self.countWords

    def countAvgMean(self):
        if self.countWords:
            self.avgMean = self.countMeans/self.countWords

    def countPercAudio(self):
        if self.countWords:
            self.percAudio = self.countAudio/self.countWords*100

    def countPercGraph(self):
        if self.countWords:
            self.percGraph = self.countGraph/self.countWords*100

    def countPercRef(self):
        if self.countWords:
            self.percRef = self.countRef/self.countWords*100


def deletedTemplates():
    deletedStrings = {}
    deletedRegexps = {}

    site = pywikibot.Site()

    # add templates in certain categories

    def getCategory(cat):
        tempDict = []
        category = pywikibot.Category(site, cat)
        if cat == u'Kategoria:Szablony odmiany':
            categoryGen = pagegenerators.CategorizedPageGenerator(category, recurse=1)
        else:
            categoryGen = pagegenerators.CategorizedPageGenerator(category)
        for template in categoryGen:
            if template.namespace() == 'Template:':
                if cat != u'Kategoria:Szablony odmiany':
                    tempDict.append(u'{{%s}}' % template.title(withNamespace=False))
                else:
                    tempDict.append(u'%s' % template.title(withNamespace=False))
        return tempDict

    deletedStrings['szablony'] = getCategory(u'Kategoria:Szablony szablonów haseł')
    deletedStrings['import'] = getCategory(u'Kategoria:Szablony automatycznych importów')
    # deletedStrings['odmiany'] = getCategory(u'Kategoria:Szablony odmiany')

    deletedStrings['others'] = []
    deletedStrings['others'].append(u'<references/>')
    deletedStrings['others'].append(u'==')
    deletedStrings['others'].append(u'\'\'przykład\'\'')
    deletedStrings['others'].append(u'krótka definicja')
    deletedStrings['others'].append(u'\n')

    deletedStrings['others'].append(u'{{niesprawdzona odmiana}}')
    deletedStrings['others'].append(u'({{termin obcy w języku polskim}})')
    deletedStrings['others'].append(u'{{podobne|')

    deletedRegexps['others'] = []
    deletedRegexps['others'].append(re.compile(ur'{{IPA([0-9]|)\|}}'))
    deletedRegexps['others'].append(re.compile(ur'\[\[[a-z]*:.*?\]\]'))
    deletedRegexps['others'].append(re.compile(ur'\'\'przykład\'\'.*?→ tłumaczenie'))
    deletedRegexps['others'].append(re.compile(ur'\* angielski: \[\[ \]\]'))

    # Polish translations
    deletedRegexps['others'].append(re.compile(u'{{tłumaczenia}}.*?{{źródła}}', re.DOTALL))

    # meanings - empty ": (1.1)" default in a new page template
    deletedRegexps['others'].append(re.compile(ur':(\s*|)\(1\.1\)(\s*|)\n'))

    # {{niesprawdzona odmiana}}
    deletedRegexps['others'].append(re.compile(ur'{{niesprawdzona odmiana.*?\n'))

    # imports with parameters
    deletedRegexps['import'] = []
    deletedRegexps['import'].append(re.compile(ur'{{[iI]mportIA\|[^}]*}}'))
    deletedRegexps['import'].append(re.compile(ur'{{importEnWikt\|[^}]*}}'))

    # multimedia
    deletedRegexps['others'].append(re.compile(ur'(\[\[(\s*|)((P|p)lik|(F|f)ile|(M|m)edia|(I|i)mage|(G|g)rafika)(\s*|):.[^\|]*|(thumb\||[0-9]*px\||right\||left\||)|{{litera)'))

    return deletedStrings, deletedRegexps


def countLength(content, templates):
    """Count the number of characters in a dictionary entry

    It's not as trivial as len(content), because it would be unfair for some languages that don't get as much bot
    attention as others. Currently, all section templates are removed before counting, as well as auto import templates.
    Also, for inflection templates (declination, conjugation, etc.) only parameter values are taken into account, not
    parameter names

    Args:
    content (unicode): the content of the page

    templates[0] (a list of unicodes): a list of strings to delete prepared in another function (because it involves
    fetching pages from a category and takes time

    templates[1] (a list of compiled regexps): as above, but these are regexps, for example import template
    {{importEnWikt}} with a parameter

    Returns:
    (int): the length of the page after removing all automatic content
    """

    strings = templates[0]
    regexps = templates[1]

    temp = content

    '''the following is for templates in [[Category: Szablony odmiany]], i.e. for tables of inflected forms
    (declination, conjugation etc.) they contain many explicitly named parameters, so only parameter values count
    towards the total length'''
    if u'odmiana-' in content:
        parsed = mwparserfromhell.parse(content)
        tempsFound = parsed.filter_templates()
        for t in tempsFound:
            if u'odmiana-' in t.name:
                temp = temp.replace(unicode(t), ''.join(unicode(param.value) for param in t.params))

    for key in regexps:
        for regex in regexps[key]:
            temp = re.sub(regex, u'', temp)

    for key in strings:
         for each in strings[key]:
            temp = temp.replace(each, u'')

    return len(temp)


def countAudio(input_text):

    counter = 0.0
    wymowa = re.compile(u'{{audio.*?}}')
    s_audio = re.findall(wymowa, input_text)
    if s_audio:
        counter = float(len(s_audio))

    return counter


def countGraph(input_text):

    counter = 0.0
    graph = re.compile(ur'\[\[(\s*|)((P|p)lik|(F|f)ile|(M|m)edia|(I|i)mage|(G|g)rafika)(\s*|):.*?(?=\]\]|{{litera)')
    s_graph = re.findall(graph, input_text)
    if s_graph:
        counter = float(len(s_graph))
    return counter


def licz_jezyki(dump_date):

    lista_stron2 = getListFromXML(dump_date)

    langs = getAllLanguages()
    statList = collections.defaultdict()
    for a in langs:
        if a.longName != u'termin obcy w języku polskim':
            statList[u'%s' % a.longName] = LangStats(a.longName, a.shortName)

    i = 1

    templatesToDelete = deletedTemplates()

    for a in lista_stron2:
        #if (i<1000):
            try: haslo = Haslo(a)
            except sectionsNotFound:
                pass
            except WrongHeader:
                pass
            else:
                if haslo.type != 5:
                    for b in haslo.listLangs:
                        if b.type != 2 and b.type != 3:
                            if b.langLong == u'termin obcy w języku polskim':
                                b.langLong = u'język polski'
                            if b.langLong in statList:
                                b.pola()
                                if not b.inflectedOnly:

                                    statList[u'%s' % b.langLong].addWord()
                                    statList[u'%s' % b.langLong].addLength(countLength(b.content, templatesToDelete))

                                    audiotmp = countAudio(b.content)
                                    graphtmp = countGraph(b.content)
                                    if audiotmp:
                                        statList[u'%s' % b.langLong].addAudio()
                                        statList[u'%s' % b.langLong].addAudioAll(audiotmp)
                                    if graphtmp:
                                        statList[u'%s' % b.langLong].addGraph()
                                        statList[u'%s' % b.langLong].addGraphAll(graphtmp)
                                    if b.type == 1:
                                        statList[u'%s' % b.langLong].addMeans(meanings(b.znaczeniaDetail))
                                        statList[u'%s' % b.langLong].addRef(refs(b.subSections[u'źródła'].text, templatesToDelete))

    for c in statList:
        statList[c].countAvgLen()
        statList[c].countAvgMean()
        statList[c].countPercAudio()
        statList[c].countPercGraph()
        statList[c].countPercRef()

    text = u''

    countRanks(statList)

    for c in statList:
        if statList[c].countWords:
            text += u'%s\t%.1f\t%.0f\t%.0f\t%.0f\t%.1f\t%.0f\t%.1f\t%.0f\t%.2f\t%.0f\t%.1f\t%d\t%d\t%d\t%d\t%d\t%d\t%d' % (statList[c].shortName, statList[c].avgLen, statList[c].countWords, statList[c].countLen/1000.0, statList[c].countAudio, statList[c].percAudio, statList[c].countGraph, statList[c].percGraph, statList[c].countMeans, statList[c].avgMean, statList[c].countRef, statList[c].percRef, statList[c].rank[u'countWords'], statList[c].rank[u'countMeans'], statList[c].rank[u'countLen'], statList[c].rank[u'avgLen'], statList[c].rank[u'percAudio'], statList[c].rank[u'percGraph'], statList[c].rank[u'percRef'])

    output_file = open(filename, 'w')
    output_file.write(text.encode("utf-8"))
    output_file.close()

    return statList


def meanings(input):
    """counting different meanings in each page
    """

    re_count = re.compile('(\: \([0-9]\.[0-9]\))')
    counter = 0.0

    if input:
        for elem in input:
            if u'{{forma' in elem[0]:
                continue
            else:
                s_count = re.findall(re_count, elem[1])
                counter += len(s_count)*1.0

    return counter


def refs(inputSection, templatesToDelete):
    """Detects references in "References" subsection of a page

    Args:
        inputSection (str): contents of {{źródła}} (references) subsection.
        templatesToDelete: precompiled regexps and strings to delete from the content before finding refs. Currently these are {{Import...}}
                           templates that are added by bots and thus shouldn't be counted as proper refs

    Returns:
        (float) 0.0 or 1.0. If, after removing templates, there are any [a-z] characters, it means there are sources that were added by humans

    """

    importTemplates = templatesToDelete[0]['import']  # these are templates that do not take any arguments so we can simply string.replace() them
    importRegexps = templatesToDelete[1]['import']  # these take arguments so we need to re.sub them

    for template in importTemplates:
        inputSection = inputSection.replace(template, u'')

    for regex in importRegexps:
        inputSection = re.sub(regex, u'', inputSection)

    re_az = re.compile('[a-z]')
    s_temp = re.search(re_az, inputSection)  #search for [a-z] in the remaining text (after deleting templates). This should (?) mean there are some human-entered sources

    if s_temp:
        return 1.0

    return 0.0


def countAll(langStat):

    words = 0
    length = 0
    audio = 0
    graph = 0
    allaudio = 0
    allgraphs = 0
    means = 0
    ref = 0
    percGraph = 0.0
    percAudio = 0.0
    avgMean = 0.0

    for a in langStat:
        words += langStat[a].countWords
        length += langStat[a].countLen
        audio += langStat[a].countAudio
        graph += langStat[a].countGraph
        allaudio += langStat[a].countAudioAll
        allgraphs += langStat[a].countGraphAll
        means += langStat[a].countMeans
        ref += langStat[a].countRef

    if words:
        percGraph = graph/words*100
        percAudio = audio/words*100
        avgMean = means/words

    output = [words, length, means, allaudio, allgraphs, ref, percGraph, percAudio, avgMean]

    return output


def compareTwo(old, new):

    output = {u'rankWords' : 0, u'rankMeans' : 0, u'rankLen' : 0, u'rankAvgLen' : 0, u'rankAudio' : 0, u'rankGraph' : 0, u'rankRef' : 0, u'words' : 0, u'means' : 0, 'length' : 0, u'audio' : 0, u'graph' : 0, u'ref' : 0, u'avgLen' : 0.0, u'avgMean' : 0.0, u'percAudio' : 0.0, u'percGraph' : 0.0, u'percRef' : 0.0}
    output[u'rankWords'] = old.rank[u'countWords'] - new.rank[u'countWords']
    output[u'rankMeans'] = old.rank[u'countMeans'] - new.rank[u'countMeans']
    output[u'rankLen'] = old.rank[u'countLen'] - new.rank[u'countLen']
    if old.rank[u'avgLen'] == 0:
        output[u'rankAvgLen'] = 100
    else:
        output[u'rankAvgLen'] = old.rank[u'avgLen'] - new.rank[u'avgLen']
    output[u'rankAudio'] = old.rank[u'percAudio'] - new.rank[u'percAudio']
    output[u'rankGraph'] = old.rank[u'percGraph'] - new.rank[u'percGraph']
    output[u'rankRef'] = old.rank[u'percRef'] - new.rank[u'percRef']
    output[u'words'] = new.countWords - old.countWords
    output[u'means'] = new.countMeans - old.countMeans
    output[u'length'] = new.countLen - old.countLen
    output[u'audio'] = new.countAudio - old.countAudio
    output[u'graph'] = new.countGraph - old.countGraph
    output[u'ref'] = new.countRef - old.countRef
    output[u'avgMean'] = new.avgMean - old.avgMean
    output[u'avgLen'] = new.avgLen - old.avgLen
    output[u'percAudio'] = new.percAudio - old.percAudio
    output[u'percGraph'] = new.percGraph - old.percGraph
    output[u'percRef'] = new.percRef - old.percRef

    return output


def changeText(input, round):

    output = u''
    if input >= math.pow(0.1, round):
        output = u'+{n:.{x}f}'.format(n=input, x=round)
    elif input <= -math.pow(0.1, round):
        output = u'{n:.{x}f}'.format(n=input, x=round)

    return output


def stat_wikitable(old, new):

    text1 = u'{| border=0 cellspacing=0 cellpadding=0\n|\n{| class="wikitable" style="margin: 0px; text-align:right;"\n! miejsce !! zmiana'
    text2 = u'{| class="wikitable sortable autonumber" style="margin: 0 auto; white-space: nowrap"\n! język !! suma długości haseł (w tys.) !! zmiana (w tys.) !! liczba haseł\n'
    text3 = text1
    text4 = u'{| class="wikitable sortable autonumber" style="margin: 0 auto; white-space: nowrap"\n! język !! średnia długość hasła !! zmiana średniej !! liczba haseł\n'
    text5 = u'{| border=0 cellspacing=0 cellpadding=0\n|\n{| class="wikitable" style="margin: 0px; text-align:right;"\n! miejsce'
    text6 = u'{| class="wikitable sortable autonumber" style="margin: 0 auto; white-space: nowrap"\n! język !! % z grafiką !! zmiana ([[w:Punkt_procentowy|p.p.]]) !! z grafiką !! % z nagraniem !! zmiana ([[w:Punkt_procentowy|p.p.]]) !! z nagraniem !! % ze źródłem !! zmiana ([[w:Punkt_procentowy|p.p.]]) !! ze źródłem !! liczba haseł\n'
    text7 = u'{| class="wikitable sortable autonumber" style="margin: 0 auto; white-space: nowrap"\n! język !! znaczeń ogółem !! zmiana !! średnia znaczeń w haśle!! zmiana średniej\n'
    text8 = text5
    text9 = u'{{#switch:{{lc:{{{1|}}}}}'
    text10 = text9
    text11 = text9
    text12 = text9
    text13 = text9
    text14 = text9
    text15 = text9
    text16 = text9

    for i in range(51):
        for a in new:
            if new[a].rank[u'countLen'] == i:
                for b in old:
                    if a == b:
                        changes = compareTwo(old[b], new[a])
                        text1 = text1 + u'\n|-\n! %d\n! %s' % (i, changeText(changes[u'rankLen'], 0))
                        text2 = text2 + u'|-\n| [[:Kategoria:%s (indeks)|%s]]\n| align="right"| %.0f\n| align="right"| %s\n| align="right"| %.0f\n' % (new[a].shortName, new[a].shortName, new[a].countLen/1000, changeText(changes[u'len']/1000, 0), new[a].countWords)


    for i in range(51):
        for a in new:
            if new[a].rank[u'countWords'] == i:
                for b in old:
                    if a == b:
                        changes = compareTwo(old[b], new[a])
                        text5 = text5 + u'\n|-\n! %d' % (i)
                        text6 = text6 + u'|-\n| [[:Kategoria:%s (indeks)|%s]]\n| align="right"| %.1f\n| align="right"| %s\n| align="right"| %.0f\n| align="right"| %.1f\n| align="right"| %s\n| align="right"| %.0f\n| align="right"| %.1f\n| align="right"| %s\n| align="right"| %.0f\n| align="right"| %.0f\n' % (new[a].shortName, new[a].shortName, new[a].percGraph, changeText(changes[u'percGraph'], 1), new[a].countGraph, new[a].percAudio, changeText(changes[u'percAudio'], 1), new[a].countAudio, new[a].percRef, changeText(changes[u'percRef'], 1), new[a].countRef, new[a].countWords)


    for i in range(50):
        for a in new:
            if new[a].rank[u'avgLen'] == i+1:
                for b in old:
                    if a == b:
                        changes = compareTwo(old[b], new[a])
                        text3 = text3 + u'\n|-\n! %d\n! %s' % (i+1, changeText(changes[u'rankAvgLen'], 0))
                        text4 = text4 + u'|-\n| [[:Kategoria:%s (indeks)|%s]]\n| align="right"| %.1f\n| align="right"| %s\n| align="right"| %.0f\n' % (new[a].shortName, new[a].shortName, new[a].avgLen, changeText(changes[u'avgLen'], 1), new[a].countWords)

    for i in range(51):
        for a in new:
            if new[a].rank[u'countMeans'] == i:
                for b in old:
                    if a == b:
                        changes = compareTwo(old[b], new[a])
                        text8 = text8 + u'\n|-\n! %d' % (i)
                        text7 = text7 + u'|-\n| [[:Kategoria:%s (indeks)|%s]]\n| align="right"| %.0f\n| align="right"| %s\n| align="right"| %.4f\n| align="right"| %s\n' % (new[a].shortName, new[a].shortName, new[a].countMeans, changeText(changes[u'means'], 0), new[a].avgMean, changeText(changes[u'avgMean'], 4))

        site = pywikibot.getSite()
        page_dane = pywikibot.Page(site, u'Moduł:statystyka/dane')
        text_dane = page_dane.get()

    for a in new:
        for b in old:
            if a == b:
                text14 += u'\n|%s=%.1f' % (new[a].shortName, new[a].countLen)
                text15 += u'\n|%s=%.1f' % (new[a].shortName, new[a].avgLen)
                text10 += u'\n|%s=%.0f' % (new[a].shortName, new[a].countGraph)
                text11 += u'\n|%s=%.0f' % (new[a].shortName, new[a].countAudio)
                text12 += u'\n|%s=%.1f' % (new[a].shortName, new[a].percGraph)
                text13 += u'\n|%s=%.1f' % (new[a].shortName, new[a].percAudio)
                text_dane = meaningsUpdateWikitext(new[a].shortName, new[a].avgMean, text_dane)
                text16 += u'\n|%s=%.4f' % (new[a].shortName.lower(), new[a].avgMean)

    all = countAll(new)

    text_dlugosc = text2 + u'|}'
    text_srednia = text4 + u'|}'
    text_multimedia = text6 + u'|}'
    text_znaczenia = text7 + u'|}'
    text_znaczenia_template = text9 + u'\n|=%.0f\n|data=%s\n|#default=bd.\n}}' % (all[2], data_slownie)
    text_GraphCount_template = text10 + u'\n|=%.0f\n|data=%s\n|#default=bd.\n}}' % (all[4], data_slownie)
    text_AudioCount_template = text11 + u'\n|=%.0f\n|data=%s\n|#default=bd.\n}}' % (all[3], data_slownie)
    text_GraphPerc_template = text12 + u'\n|=%.1f|data=%s\n|#default=bd.\n}}' % (all[6], data_slownie)
    text_AudioPerc_template = text13 + u'\n|=%.1f|data=%s\n|#default=bd.\n}}' % (all[7], data_slownie)
    text_dlugosc_template = text14 + u'\n|=%.0f|data=%s\n|#default=bd.\n}}' % (all[1]/1000, data_slownie)
    text_srednia_template = text15 + u'\n|=|data=%s\n|#default=bd.\n}}' % (data_slownie)
    text_znaczenia_srednia_template = text16 + u'\n|=%.4f\n|data=%s\n|#default=bd.\n}}' % (all[8], data_slownie)
    text_dane = re.sub(ur'date = \'[0-9]{2}\.[0-9]{2}\.[0-9]{4}', u'date = \'%s' % data_slownie, text_dane)



    page_dlugosc = pywikibot.Page(site, u'Wikipedysta:Alkamid/statystyka/długość')
    page_srednia = pywikibot.Page(site, u'Wikipedysta:Alkamid/statystyka/długość_średnia')
    page_multimedia = pywikibot.Page(site, u'Wikipedysta:Alkamid/statystyka/multimedia')
    page_znaczenia = pywikibot.Page(site, u'Wikipedysta:AlkamidBot/statystyka/znaczenia')
    page_dlugosc_templ = pywikibot.Page(site, u'Wikipedysta:AlkamidBot/statystyka/długość/template')
    page_srednia_templ = pywikibot.Page(site, u'Wikipedysta:AlkamidBot/statystyka/długość_średnia/template')
    page_GraphCount_templ = pywikibot.Page(site, u'Wikipedysta:AlkamidBot/statystyka/liczba_grafik/template')
    page_GraphPerc_templ = pywikibot.Page(site, u'Wikipedysta:AlkamidBot/statystyka/procent_grafik/template')
    page_AudioCount_templ = pywikibot.Page(site, u'Wikipedysta:AlkamidBot/statystyka/liczba_audio/template')
    page_AudioPerc_templ = pywikibot.Page(site, u'Wikipedysta:AlkamidBot/statystyka/procent_audio/template')

    filename_dlugosc = "output/wikitable-dlugosc.txt"
    filename_srednia = "output/wikitable-srednia.txt"
    filename_multimedia = "output/wikitable-multimedia.txt"
    filename_znaczenia = "output/wikitable-znaczenia.txt"
    filename_dlugosc_old = "output/dlugosc_old_%s.txt" % (data)
    filename_srednia_old = "output/srednia_old_%s.txt" % (data)
    filename_multi_old = "output/multi_old_%s.txt" % (data)
    filename_znacz_old = "output/znacz_old_%s.txt" % (data)

    file = open(filename_dlugosc, 'w')
    file.write(text_dlugosc.encode( "utf-8" ))
    file.close
    file = open(filename_srednia, 'w')
    file.write(text_srednia.encode("utf-8"))
    file.close
    file = open(filename_multimedia, 'w')
    file.write(text_multimedia.encode("utf-8"))
    file.close
    file = open(filename_znaczenia, 'w')
    file.write(text_znaczenia.encode("utf-8"))
    file.close


    page_dlugosc.text = text_dlugosc
    page_srednia.text = text_srednia
    page_multimedia.text = text_multimedia
    page_znaczenia.text = text_znaczenia
    page_dane.text = text_dane
    page_dlugosc_templ.text = text_dlugosc_template
    page_srednia_templ.text = text_srednia_template
    page_GraphCount_templ.text = text_GraphCount_template
    page_GraphPerc_templ.text = text_GraphPerc_template
    page_AudioCount_templ.text = text_AudioCount_template
    page_AudioPerc_templ.text = text_AudioPerc_template

    if (offline_mode == 0):
        page_dlugosc.save(comment="Aktualizacja statystyk, dane z %s" % data_slownie, botflag=False)
        page_srednia.save(comment="Aktualizacja statystyk, dane z %s" % data_slownie, botflag=False)
        page_multimedia.save(comment="Aktualizacja statystyk, dane z %s" % data_slownie, botflag=False)
        page_znaczenia.save(comment="Aktualizacja statystyk, dane z %s" % data_slownie, botflag=False)
        page_dane.save(comment="Aktualizacja statystyk, dane z %s" % data_slownie)
        page_dlugosc_templ.save(comment="Aktualizacja statystyk, dane z %s" % data_slownie)
        page_srednia_templ.save(comment="Aktualizacja statystyk, dane z %s" % data_slownie)
        page_GraphCount_templ.save(comment="Aktualizacja statystyk, dane z %s" % data_slownie)
        page_GraphPerc_templ.save(comment="Aktualizacja statystyk, dane z %s" % data_slownie)
        page_AudioCount_templ.save(comment="Aktualizacja statystyk, dane z %s" % data_slownie)
        page_AudioPerc_templ.save(comment="Aktualizacja statystyk, dane z %s" % data_slownie)
    else:
        file = codecs.open('outstat.txt', 'w')
        myout = text_dlugosc + u'\n\n\n' + text_srednia + u'\n\n\n' + text_multimedia + u'\n\n\n' + text_znaczenia + u'\n\n\n' + text_dane + u'\n\n\n' + text_dlugosc_template + u'\n\n\n' + text_srednia_template + u'\n\n\n' + text_GraphCount_template + u'\n\n\n' + text_GraphPerc_template + u'\n\n\n' + text_AudioCount_template + u'\n\n\n' + text_AudioPerc_template
        file.write(myout.encode('utf-8'))
        file.close()


def dlaczego(new):
    site = pywikibot.getSite()
    dlaczego_strona = pywikibot.Page(site, u'Wikisłownik:Dlaczego Wikisłownik')
    presskit = pywikibot.Page(site, u'Wikisłownik:Presskit')

    all = countAll(new)

    audioCount = all[3]
    graphCount = all[4]
    audioCount /= 100
    audioCount = int(math.floor(audioCount))
    audioCount *= 100
    graphCount /= 100
    graphCount = int(math.floor(graphCount))
    graphCount *= 100

    for elem in new:
        if new[elem].rank['percAudio'] == 1:
            audioName1 = new[elem].shortName
            audioPerc1 = int(new[elem].percAudio)
        elif new[elem].rank['percAudio'] == 2:
            audioName2 = new[elem].shortName
            audioPerc2 = int(new[elem].percAudio)
        elif new[elem].rank['percAudio'] == 3:
            audioName3 = new[elem].shortName
            audioPerc3 = int(new[elem].percAudio)

    dlaczegoText = dlaczego_strona.get()
    presskitText = presskit.get()
    dlaczegoText = re.sub(ur'w Wikisłowniku znajdziesz ponad \'\'\'[0-9]* nagrań wymowy\'\'\' w wielu językach', u'w Wikisłowniku znajdziesz ponad \'\'\'%s nagrań wymowy\'\'\' w wielu językach' % audioCount, dlaczegoText)
    dlaczegoText = re.sub(ur'najwięcej plików z wymową posiadają języki:.*?\n', u'najwięcej plików z wymową posiadają języki: %s (%d%%), %s (%d%%) oraz %s (%d%%)\n' % (audioName1, audioPerc1, audioName2, audioPerc2, audioName3, audioPerc3), dlaczegoText)
    dlaczegoText = re.sub(ur'w hasłach znajdziesz \'\'\'ilustracje\'\'\' \(ponad [0-9]*\)', u'w hasłach znajdziesz \'\'\'ilustracje\'\'\' (ponad %d)' % graphCount, dlaczegoText)
    presskitText = re.sub(ur'ponad [0-9]* nagrań wymowy', u'ponad %d nagrań wymowy' % audioCount, presskitText)
    presskitText = re.sub(ur'ponad [0-9]* ilustracji', u'ponad %d ilustracji' % graphCount, presskitText)

    if offline_mode == 0:
                dlaczego_strona.text = dlaczegoText
                dlaczego_strona.save(comment=u'aktualizacja', botflag=True)
                presskit.text = presskitText
                presskit.save(comment=u'aktualizacja', botflag=True)


def meaningsUpdateWikitext(lang, mean, text):

    regex = re.compile(ur'({\s*?\'%s\'\s*,\s*{[\w\s,=\']*?)(z\s*=\s*[0-9\.]*)([\w\s,=\']*?})' % re.escape(lang), re.UNICODE)
    s = re.search(regex, text)
    if s and s.group(2):
        text = re.sub(regex, ur'\1z = %.4f\3' % mean, text)
    else:
        regex = re.compile(ur'({\s*?\'%s\')\s*(,\s*{)*' % re.escape(lang), re.UNICODE)
        s = re.search(regex, text)
        if s:
            if s.group(2):
                text = re.sub(regex, ur'\1\2 z = %.4f,' % mean, text)
            else:
                text = re.sub(regex, ur'\1, { z = %.4f } ' % mean, text)
    return text


def data_stat():

    site = pywikibot.getSite()
    stat = pywikibot.Page(site, u'Wikisłownik:Statystyka')

    re_przed = re.compile(u'(.*Zestawienie obejmuje 50 największych \(posiadających najwięcej haseł\) języków na Wikisłowniku. Zanalizowano stan na dzień )', re.DOTALL)
    re_po = re.compile(u'.*Zestawienie obejmuje 50 największych \(posiadających najwięcej haseł\) języków na Wikisłowniku. Zanalizowano stan na dzień.*?(.\n.*)', re.DOTALL)

    s_przed = re.search(re_przed, stat.get())
    s_po = re.search(re_po, stat.get())

    final = s_przed.group(1) + data_slownie + u', a zmiany podano w stosunku do ' + data_old_slownie + s_po.group(1)

    if offline_mode:
        print final
    else:
                stat.text = final
        stat.save(comment=u'zmiana daty')


def statystyka(oldDate, newDate):
    global offline_mode
    offline_mode = 0
    global filename
    filename = "output/statystykanowa.txt"
    global data
    data = newDate
    global data_old
    data_old = oldDate
    global data_slownie
    data_slownie = data[6] + data[7] + u'.' + data[4] + data[5] + u'.' + data[0] + data[1] + data[2] + data[3]
    global data_old_slownie
    data_old_slownie = data_old[6] + data_old[7] + u'.' + data_old[4] + data_old[5] + u'.' + data_old[0] + data_old[1] + data_old[2] + data_old[3]
    file = open(filename, 'w')
    file.close

    new = licz_jezyki(data)
    old = licz_jezyki(data_old)

    stat_wikitable(old, new)
    dlaczego(new)
    writeRCLimit(u'statystyka', data) #save the date - will be used as the last update date in the next run
    data_stat()
