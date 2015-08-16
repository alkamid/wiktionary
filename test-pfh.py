#!/usr/bin/python
# -*- coding: utf-8 -*-

from klasa import *
import pywikibot
import collections

def licz_jezyki():

    lista_stron2 = ['bīhi sà bòlo', 'ʘna̰e']

    statList = collections.defaultdict()
    statList["język !Xóõ"] = LangStats("język !Xóõ", "!Xóõ")

    i = 1

    #templatesToDelete = deletedTemplates()

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
                        print(b.langLong)
                        if b.langLong == 'termin obcy w języku polskim':
                            b.langLong = 'język polski'
                        if b.langLong in statList:
                            b.pola()

                            if not b.inflectedOnly:

                                statList['%s' % b.langLong].addWord()
                                #statList[u'%s' % b.langLong].addLength(countLength(b.content, templatesToDelete))

                                #audiotmp = countAudio(b.content)
                                #graphtmp = countGraph(b.content)
                                #if audiotmp:
                                #    statList[u'%s' % b.langLong].addAudio()
                                #    statList[u'%s' % b.langLong].addAudioAll(audiotmp)
                                #if graphtmp:
                                #    statList[u'%s' % b.langLong].addGraph()
                                #    statList[u'%s' % b.langLong].addGraphAll(graphtmp)
                                if b.type == 1:
                                    print(meanings(b.znaczeniaDetail))
                                    print('here')
                                    statList['%s' % b.langLong].addMeans(meanings(b.znaczeniaDetail))
                                    #statList[u'%s' % b.langLong].addRef(refs(b.subSections[u'źródła'].text, templatesToDelete))
                                else:
                                    print(b.type)

    #statList[u"język !Xóõ"].countAvgMean()
    print(statList["język !Xóõ"].countWords)
    print(statList["język !Xóõ"].countMeans)

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
        self.rank = {'countWords': 0, 'countMeans': 0, 'countLen': 0, 'avgLen': 0, 'percAudio': 0, 'percGraph': 0, 'percRef': 0}

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

def meanings(input):
    """counting different meanings in each page
    """

    re_count = re.compile('(\: \([0-9]\.[0-9]\))')
    counter = 0.0

    if input:
        for elem in input:
            if '{{forma' in elem[0]:
                continue
            else:
                s_count = re.findall(re_count, elem[1])
                counter += len(s_count)*1.0

    return counter




licz_jezyki()
