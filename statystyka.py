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
		self.rank = {u'countWords' : 0, u'countMeans' : 0, u'countLen' : 0, u'avgLen' : 0, u'percAudio' : 0, u'percGraph' : 0, u'percRef' : 0}
		
	def addLength(self, len):
		self.countLen += len
		
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

def CountLength(input):
	
	usun = []
	usun.append(u'{{odmiana}}')
	usun.append(u'{{etymologia}}')
	usun.append(u'{{wymowa}}')
	usun.append(u'{{znaczenia}}')
	usun.append(u'{{przykłady}}')
	usun.append(u'{{składnia}}')
	usun.append(u'{{kolokacje}}')
	usun.append(u'{{pokrewne}}')
	usun.append(u'{{frazeologia}}')
	usun.append(u'{{uwagi}}')
	usun.append(u'{{synonimy}}')
	usun.append(u'{{antonimy}}')
	usun.append(u'{{hiperonimy}}')
	usun.append(u'{{hiponimy}}')
	usun.append(u'{{holonimy}}')
	usun.append(u'{{meronimy}}')
	usun.append(u'{{źródła}}')
	usun.append(u'{{czytania}}')
	usun.append(u'{{determinatywy}}')
	usun.append(u'{{hanja}}')
	usun.append(u'{{hanja-kreski}}')
	usun.append(u'{{klucz}}')
	usun.append(u'{{kreski}}')
	usun.append(u'{{pochodne}}')
	usun.append(u'{{pole}}')
	usun.append(u'{{trans}}')
	usun.append(u'{{transkr}}')
	usun.append(u'{{transliteracja}}')
	usun.append(u'{{transkrypcja}}')
	usun.append(u'{{warianty}}')
	usun.append(u'{{zapis hieroglificzny}}')
	usun.append(u'{{zch-etymologia}}')
	usun.append(u'{{zch-klucz}}')
	usun.append(u'{{zch-kody}}')
	usun.append(u'{{zch-kolejność}}')
	usun.append(u'{{zch-kreski}}')
	usun.append(u'{{zch-uwagi}}')
	usun.append(u'{{zch-warianty}}')
	usun.append(u'{{zch-znaczenia}}')
	usun.append(u'{{znak-zch}}')
	usun.append(u'{{złożenia}}')
	usun.append(u'<references/>')
	usun.append(u'==')
	usun.append(u'{{IPA([0-9]|)\|}}')
	usun.append(u'\[\[[a-z]*\:.*?\]\]')
	usun.append(u'\'\'przykład\'\'')
	usun.append(u'krótka definicja')
	usun.append(u'\'\'przykład\'\'.*?→ tłumaczenie')
	usun.append(u'\* angielski\: \[\[ \]\]')
	usun.append(u'\n')
        
        #add all import templates 
	site = pywikibot.Site()
        importCategory = pywikibot.Category(site, u'Kategoria:Szablony automatycznych importów')
        importCategoryGen = pagegenerators.CategorizedPageGenerator(importCategory)
        for template in importCategoryGen:
                if template.namespace() == 'Template:':
                        usun.append(u'{{%s}}' % template.title(withNamespace=False))

       
	usun.append(u'{{niesprawdzona odmiana}}')
	usun.append(u'({{termin obcy w języku polskim}})')
	usun.append(u'{{Rzeczownik języka polskiego')
	usun.append(u'\|Mianownik lp \=')
	usun.append(u'\|Mianownik lm \=')
	usun.append(u'\|Dopełniacz lp \=')
	usun.append(u'\|Dopełniacz lm \=')
	usun.append(u'\|Celownik lp \=')
	usun.append(u'\|Celownik lm \=')
	usun.append(u'\|Biernik lp \=')
	usun.append(u'\|Biernik lm \=')
	usun.append(u'\|Narzędnik lp \=')
	usun.append(u'\|Narzędnik lm \=')
	usun.append(u'\|Miejscownik lp \=')
	usun.append(u'\|Miejscownik lm \=')
	usun.append(u'\|Wołacz lp \=')
	usun.append(u'\|Wołacz lm \=')
	usun.append(u'{{podobne\|')
	
	sekcja = re.compile(u'==\s*.*?\(\{\{.*?(\|.*?\}\}\)|\}\}\))\s*?==')
	
	#poniższe chwilowo nie ma zastosowania, ale można jakoś skompresować szukanie multimediów
	'''
	grafika = []
	grafika.append(u'\[\[\s*(G|g)rafika\s*\:.*?\]\]')
	grafika.append(u'\[\[\s*(I|i)mage\s*\:.*?\]\]')
	grafika.append(u'\[\[\s*(M|m)edia\s*\:.*?\]\]')
	grafika.append(u'\[\[\s*(F|f)ile\s*\:.*?\]\]')
	grafika.append(u'\[\[\s*(P|p)lik\s*\:.*?\]\]')
	grafika_join = '|'.join(map(re.escape,grafika))	
	'''
	
	polski = re.compile(u'{{tłumaczenia}}.*', re.DOTALL)
	
	znaczenia = re.compile(ur':(\s*|)\(1\.1\)(\s*|)\n')
	niesprawdzonaOdmiana = re.compile(ur'{{niesprawdzona odmiana.*?\n')
	importIA = re.compile(ur'{{[iI]mportIA\|[^}]*}}')
        importEnWikt = re.compile(ur'{{importEnWikt\|[^}]*}}')
	jidysz = re.compile(ur'{{jidysz\|[^}]*}}')
	greka = re.compile(ur'{{greka\|[^}]*}}')
	linki = re.compile(ur'\[\[[^]]*?\|')
	
	usun_join ='|'.join(map(re.escape, usun))

#TODO: zobaczyć czy usuwa nagłówki z parametrem	
	temp = re.sub(sekcja, u'', input)
	temp = re.sub(usun_join, u'', temp)
	temp = re.sub(znaczenia, u'', temp)
	temp = re.sub(niesprawdzonaOdmiana, u'', temp)
	temp = re.sub(polski, '', temp)
	temp = re.sub(u'(\[\[(\s*|)((P|p)lik|(F|f)ile|(M|m)edia|(I|i)mage|(G|g)rafika)(\s*|):.[^\|]*|(thumb\||[0-9]*px\||right\||left\||)|{{litera)', '', temp)

	temp = re.sub(importIA, u'', temp)
	temp = re.sub(importEnWikt, u'', temp)
	temp = re.sub(jidysz, u'', temp)
	temp = re.sub(greka, u'', temp)		
	temp = re.sub(linki, u'[[', temp)
	
	return len(temp)

def countAudio(input):
	
	counter = 0.0
	wymowa = re.compile(u'{{audio.*?}}')
	s_audio = re.findall(wymowa, input)
	if s_audio:
		counter = float(len(s_audio))
	
	return counter

def countGraph(input):
	
	counter = 0.0
	graph = re.compile(ur'\[\[(\s*|)((P|p)lik|(F|f)ile|(M|m)edia|(I|i)mage|(G|g)rafika)(\s*|):.*?(?=\]\]|{{litera)')
	s_graph = re.findall(graph, input)
	if s_graph:
		counter = float(len(s_graph))
	return counter
	

def licz_jezyki(data):
	
	lista_stron2 = getListFromXML(data)
	
	langs = getAllLanguages()
	statList = collections.defaultdict()
	for a in langs:
		if a.longName != u'termin obcy w języku polskim':
			statList[u'%s' % a.longName] = LangStats(a.longName, a.shortName)
	
	i = 1
	
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
                                        #print haslo.title
                                        if b.type != 2 and b.type != 3:
                                                if b.langLong == u'termin obcy w języku polskim':
                                                        b.langLong = u'język polski'
                                                if b.langLong in statList:
                                                        b.pola()
                                                        if not b.inflectedOnly:
                                                                
                                                                statList[u'%s' % b.langLong].addWord()
                                                                statList[u'%s' % b.langLong].addLength(CountLength(b.content))

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
                                                                        statList[u'%s' % b.langLong].addRef(refs(b.subSections[u'źródła']))

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
	
	file = open(filename, 'w')
	file.write(text.encode( "utf-8" ))
	file.close
	
	return statList
	
def meanings(input):
	#counting different meanings in each page
	
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


def refs(inputZrodla):
	#counting references
	
	re_az = re.compile('[a-z]')

	s_temp = re.search(re_az, inputZrodla)
        if s_temp:
                return 1.0
        else:
                return 0.0

	return 0


def countAll(langStat):
	
	words = 0
	len = 0
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
		len += langStat[a].countLen
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
	
	output = [words, len, means, allaudio, allgraphs, ref, percGraph, percAudio, avgMean]
		
	return output

def compareTwo(old, new):
	
	output = {u'rankWords' : 0, u'rankMeans' : 0, u'rankLen' : 0, u'rankAvgLen' : 0, u'rankAudio' : 0, u'rankGraph' : 0, u'rankRef' : 0, u'words' : 0, u'means' : 0, 'len' : 0, u'audio' : 0, u'graph' : 0, u'ref' : 0, u'avgLen' : 0.0, u'avgMean' : 0.0, u'percAudio' : 0.0, u'percGraph' : 0.0, u'percRef' : 0.0}
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
	output[u'len'] = new.countLen - old.countLen
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
	#poniżej text2 jeśli ma być miejsce w rankingu i zmiana tego miejsca
	#text2 = u'\n|}\n|\n{| class="wikitable sortable" style="margin: 0 auto; white-space: nowrap"\n! język !! suma długości haseł (w tys.) !! zmiana (w tys.) !! liczba haseł\n'
	text3 = text1
	text4 = u'{| class="wikitable sortable autonumber" style="margin: 0 auto; white-space: nowrap"\n! język !! średnia długość hasła !! zmiana średniej !! liczba haseł\n'
	#text4 = u'\n|}\n|\n{| class="wikitable sortable" style="margin: 0 auto; white-space: nowrap"\n! język !! średnia długość hasła !! zmiana średniej !! liczba haseł\n'
	text5 = u'{| border=0 cellspacing=0 cellpadding=0\n|\n{| class="wikitable" style="margin: 0px; text-align:right;"\n! miejsce'
	text6 = u'{| class="wikitable sortable autonumber" style="margin: 0 auto; white-space: nowrap"\n! język !! % z grafiką !! zmiana ([[w:Punkt_procentowy|p.p.]]) !! z grafiką !! % z nagraniem !! zmiana ([[w:Punkt_procentowy|p.p.]]) !! z nagraniem !! % ze źródłem !! zmiana ([[w:Punkt_procentowy|p.p.]]) !! ze źródłem !! liczba haseł\n'
	#text6 = u'\n|}\n|\n{| class="wikitable sortable" style="margin: 0 auto; white-space: nowrap"\n! język !! % z grafiką !! zmiana % !! z grafiką !! % z nagraniem !! zmiana % !! z nagraniem !! % ze źródłem !! zmiana % !! ze źródłem !! liczba haseł\n'
	text7 = u'{| class="wikitable sortable autonumber" style="margin: 0 auto; white-space: nowrap"\n! język !! znaczeń ogółem !! zmiana !! średnia znaczeń w haśle!! zmiana średniej\n'
	#text7 = u'\n|}\n|\n{| class="wikitable sortable" style="margin: 0 auto; white-space: nowrap"\n! język !! znaczeń ogółem !! zmiana !! średnia znaczeń w haśle!! zmiana średniej\n'
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
				text14 = text14 + u'\n|%s=%.1f' % (new[a].shortName, new[a].countLen)
				text15 = text15 + u'\n|%s=%.1f' % (new[a].shortName, new[a].avgLen)
				text10 = text10 + u'\n|%s=%.0f' % (new[a].shortName, new[a].countGraph)
				text11 = text11 + u'\n|%s=%.0f' % (new[a].shortName, new[a].countAudio)
				text12 = text12 + u'\n|%s=%.1f' % (new[a].shortName, new[a].percGraph)
				text13 = text13 + u'\n|%s=%.1f' % (new[a].shortName, new[a].percAudio)
				#text9 = text9 + u'\n|%s=%.0f' % (new[a].shortName.lower(), new[a].countMeans)
                                text_dane = meaningsUpdateWikitext(new[a].shortName, new[a].avgMean, text_dane)
                                text16 = text16 + u'\n|%s=%.4f' % (new[a].shortName.lower(), new[a].avgMean)
		
	
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

	audioCount = 0
	graphCount = 0
	all = countAll(new)
	
	audioCount = all[3]
	graphCount = all[4]
	audioCount/=100
	audioCount = int(math.floor(audioCount))
	audioCount*=100
	graphCount/=100
	graphCount = int(math.floor(graphCount))
	graphCount*=100
	
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
		
def licznik():
	site = pywikibot.getSite()
	lista_stron = getListFromXML(data)
	dlaczego_strona = pywikibot.Page(site, u'Wikisłownik:Dlaczego Wikisłownik')
	presskit = pywikibot.Page(site, u'Wikisłownik:Presskit')
	liczba_znakow = 0.0
	liczba_slow = 0.0
	liczba_audio = 0
	liczba_grafik = 0

	re_audio = re.compile(u'{{audio.*?}}')
	re_grafika = re.compile(ur'\[\[(\s*|)((P|p)lik|(F|f)ile|(M|m)edia|(I|i)mage|(G|g)rafika)(\s*|):')
	grafika = []
	grafika.append(u'\[\[Grafika:.*?\]\]')
	grafika.append(u'\[\[Image:.*?\]\]')
	grafika.append(u'\[\[Media:.*?\]\]')
	grafika.append(u'\[\[File:.*?\]\]')
	grafika.append(u'\[\[Plik:.*?\]\]')
	dlaczego_przed = re.compile(u'(.*=== Multimedia ===\n\[\[Plik\:Crystal Clear app voice\-support\.png\|right\|100px\]\]\n\* na Wikisłowniku znajdziesz ponad \'\'\')', re.DOTALL)
	dlaczego_po = re.compile(u'(\), które ułatwiają zapamiętywanie nowych słów oraz pokazują to, co często trudno opisać słowami.*)', re.DOTALL)
	dlaczego_proc = re.compile(u'\* plik z wymową posiada(.*?)% angielskich')

	grafika_join = '|'.join(map(re.escape,grafika))

	for page in lista_stron:

		try:
			text = page.text
		except pywikibot.NoPage:
			print u'strona nie istnieje'
		except pywikibot.IsRedirectPage:
			print u'%s - przekierowanie' % (page.title())
		except pywikibot.Error:
			print u'nieznany błąd'
		
		liczba_audio += len(re.findall(audio, text))
		liczba_grafik += len(re.findall(u'\[\[(\s*|)((P|p)lik|(F|f)ile|(M|m)edia|(I|i)mage|(G|g)rafika)(\s*|):', text))

	dodaj = "audio: %d, grafiki: %d" % (liczba_audio, liczba_grafik)

	dlaczego_przed_s = re.search(dlaczego_przed, dlaczego_strona.get())
	dlaczego_po_s = re.search(dlaczego_po, dlaczego_strona.get())
	dlaczego_proc_s = re.search(dlaczego_proc, dlaczego_strona.get())

	liczba_audio = liczba_audio/100
	liczba_audio = math.floor(liczba_audio)
	liczba_audio = liczba_audio*100
	liczba_grafik = liczba_grafik/100
	liczba_grafik = math.floor(liczba_grafik)
	liczba_grafik = liczba_grafik*100


	tekst = u''
	if dlaczego_przed_s != None and dlaczego_po_s != None and dlaczego_proc_s:
		tekst = dlaczego_przed_s.group(1)
		tekst = tekst + u'%d' % liczba_audio
		tekst = tekst + u' nagrań wymowy\'\'\' w wielu językach (na przykład w [[solder|angielskim]], [[акация|rosyjskim]], [[können|niemieckim]] czy [[trzydzieści|polskim]]) wykonanych przez osoby używające danego języka jako ojczystego. To jedyny taki słownik w Internecie!\n* plik z wymową posiada'
		tekst = tekst + dlaczego_proc_s.group(1)
		tekst = tekst + u'% angielskich\n* nagrania można ściągnąć na dysk lub [[:Grafika:En-uk-ubiquitous.ogg|odsłuchać w przeglądarce]]\n* Wikisłownik to słownik multimedialny &mdash; w hasłach znajdziesz \'\'\'ilustracje\'\'\' (ponad '
		tekst = tekst + u'%d' % liczba_grafik
		tekst = tekst + dlaczego_po_s.group(1)
	else:
		print u'coś poszło nie tak\n'
	
	if offline_mode:
		pass
		#print tekst
	else:
                dlaczego_strona.text = tekst
		dlaczego_strona.save(comment = u'Aktualizacja z ostatniego zrzutu bazy danych (%s)' % data_slownie, botflag=False)
		#dlaczego_strona.put(tekst, comment = u'Aktualizacja z ostatniego zrzutu bazy danych (%s)' % data_slownie)
	
	re_presskit_przed = re.compile(u'(.*\* najwięcej słów jest w języku angielskim; następne pod względem liczby są: język polski i sztuczny język interlingua)', re.DOTALL) 
	re_presskit_po = re.compile(u'(== Błędne opinie o Wikisłowniku ==.*)', re.DOTALL)
	
	s_presskit_przed = re.search(re_presskit_przed, presskit.get())
	s_presskit_po = re.search(re_presskit_po, presskit.get())
		
	presskit_tekst = u''
	if s_presskit_przed and s_presskit_po:
		presskit_tekst = s_presskit_przed.group(1)
		presskit_tekst = presskit_tekst + u'\n* ponad %d nagrań wymowy\n* ponad %d ilustracji\n\n' % (liczba_audio, liczba_grafik)
		presskit_tekst = presskit_tekst + s_presskit_po.group(1)
	else:
		print u'coś poszło nie tak\n'
		
	if offline_mode:
		print presskit_tekst
	else:
                presskit.text = presskit_tekst
		presskit.save(comment = u'Aktualizacja z ostatniego zrzutu bazy danych (%s)' % data_slownie, botflag=False)
		#presskit.put(presskit_tekst, comment = u'Aktualizacja z ostatniego zrzutu bazy danych (%s)' % data_slownie)

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
	#licznik()
	writeRCLimit(u'statystyka', data) #save the date - will be used as the last update date in the next run
	data_stat()
	
