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
import config
from pywikibot import xmlreader
import bz2
import sys
from pywikibot.data.api import Request
from os import environ
import mwparserfromhell

def parseTitle(title):
    site = pywikibot.Site()
    page = pywikibot.Page(site, title)
    text = page.get()
    return mwparserfromhell.parse(text)

def parseText(text):
    return mwparserfromhell.parse(text)

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
	regex['langs-wstepna'] = re.compile(ur'(.*?)==', re.DOTALL)
	regex['langs-lang'] = re.compile(ur'(== .*?\(\{\{.*?\}\}\) ==.*?)(?=$|[^{{]==)', re.DOTALL)
	def __init__(self, title, text='faoweoucmo3u4210987acskjdh', new=False):
            if new == True:
                self.site = pywikibot.Site('pl', 'wiktionary')
                self.type = 3
                self.title = title
                self.wstepna = u''
                self.content = u''
                self.listLangs = []
            elif type(title) is str:
                self.site = pywikibot.Site('pl', 'wiktionary')
                self.type = 1
                self.title = title
                self.wstepna = u''
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
                    if page.namespace() and u'Wikipedysta:AlkamidBot/sjp/' not in self.title:
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
		s_wstepna = re.search(self.regex['langs-wstepna'], self.content)
		if s_wstepna:
			self.wstepna = s_wstepna.group(1)
		else:
			self.wstepna = u''
		
		s_lang = re.findall(self.regex['langs-lang'], self.content)
		if s_lang:
			for b in s_lang:
				self.listLangs.append(Sekcja(b, self.title))
		else:
			self.type = 4
			raise sectionsNotFound
		
	def push(self, offline=False, myComment = u'', new=False):
		
		toPush = self.wstepna
		sthWrong = 0
		if not ':' in self.title:
			self.listLangs = sortSections(self.listLangs)
		for a in self.listLangs:
			if a.type in (2,3,7):
				sthWrong = 1
			toPush += a.header + u'\n' + a.content.strip() + u'\n\n'
		toPush = toPush.strip()
		if not sthWrong:
			if offline:
				print toPush
			else:
				page = pywikibot.Page(self.site, self.title)
				try: content = page.get()
				except pywikibot.IsRedirectPage:
					print u'%s - konflikt edycji' % self.title
				except pywikibot.NoPage:
					if new:
						page.put(toPush, comment=myComment)
				except pywikibot.Error:
					print u'%s - konflikt edycji' % self.title
				else:
					if content == self.content and content != toPush:
						page.put(toPush, comment=myComment)
					elif content != self.content:
						print u'%s - konflikt edycji' % self.title
	def addSection(self, section):
		self.listLangs.append(section)
							
def sortSections(sectionList):
	# sorting sections. The proper order is: 1. "użycie międzynarodowe" 2. "polski" 3. "termin obcy w języku polskim" 4. "znak chiński". The rest is sorted alphabetically with pl_PL locale
	sectionList = sorted(sectionList, cmp=lambda a, b: locale.strcoll(a.lang, b.lang))
	for sec in sectionList:
		if sec.lang == u'znak chiński':
			ind = sectionList.index(sec)
			sectionList.insert(0, sectionList.pop(ind))
	for sec in sectionList:
		if sec.lang == u'termin obcy w języku polskim':
			ind = sectionList.index(sec)
			sectionList.insert(0, sectionList.pop(ind))
	for sec in sectionList:
		if sec.lang == u'polski':
			ind = sectionList.index(sec)
			sectionList.insert(0, sectionList.pop(ind))
	for sec in sectionList:
		if sec.lang == u'użycie międzynarodowe':
			ind = sectionList.index(sec)
			sectionList.insert(0, sectionList.pop(ind))
	return sectionList
		
class notFromMainNamespace(Exception):
	def __init__(self):
	   self.value = u'not from main namespace!'
	def __str__(self):
		return repr(self.value)
	
class sectionsNotFound(Exception):
	def __init__(self):
	   self.value = u'language sections not found!'
	def __str__(self):
		return repr(self.value)
	
class DumpNotFound(Exception):
	def __init__(self):
	   self.value = u'the latest dump has not been found'
	def __str__(self):
		return repr(self.value)	
	
class WrongHeader(Exception):
	def __init__(self):
	   self.value = u'something is wrong with the header'
	def __str__(self):
		return repr(self.value)

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
#11 - chiński standardowy - przekierowanie do ekwiwalentu uproszczonego
#12 - esperanto
#13 - ancient egyptian
#14 - numbering of meanings is wrong
#TODO: numerek dla każdego z typów

class subSection():
    def __init__(self, name, optional=0):
        self.name = name
        self.optional = optional

		
class Sekcja():
	regex = {}
	regex['init-lang'] = re.compile(ur'== (.*?) \(\{\{(język |)(.*?)(?=\|(.*?)\}\}\) ==|\}\}\) ==)')
	regex['init-langLong'] = re.compile(ur'== (.*?) \(\{\{(.*?)(\|.*?\}\}\) ==|\}\}\) ==)')
	regex['init-headerAndContent'] = re.compile(ur'\s*(== .*? \({{.*?}}\) ==)[ ]*\n(.*)', re.DOTALL)
	

	regex['pola-dodatki'] = re.compile(ur'(.*?)(\n|){{wymowa}}', re.DOTALL)
	regex['pola-wymowa'] = re.compile(u'{{wymowa}}(.*?)\n{{znaczenia}}', re.DOTALL)
	regex['pola-znaczeniaWhole'] = re.compile(u'{{znaczenia}}(.*?)\n{{odmiana}}', re.DOTALL)
	regex['pola-znaczeniaDetail'] = re.compile(ur'\n\s*?(\'\'.*?|{{forma rzeczownika.*?|{{forma przymiotnika.*?|{{forma czasownika.*?|{{przysłowie .*?|{{morfem\|.*?)\s*?(\n\s*?\: \([0-9]\.[0-9]\.*[0-9]*\).*?)(?=\n\'\'|\n{{forma rzeczownika|\n{{forma przymiotnika|\n{{forma czasownika|\n{{przysłowie|\n{{morfem\||$)', re.DOTALL)
	regex['pola-odmiana'] = re.compile(u'{{odmiana}}(.*?)\n{{przykłady}}', re.DOTALL)
	regex['pola-przyklady'] = re.compile(u'{{przykłady}}(.*?)\n{{składnia}}', re.DOTALL)
	regex['pola-skladnia'] = re.compile(u'{{składnia}}(.*?)\n{{kolokacje}}', re.DOTALL)
	regex['pola-kolokacje'] = re.compile(u'{{kolokacje}}(.*?)\n{{synonimy}}', re.DOTALL)
	regex['pola-synonimy'] = re.compile(u'{{synonimy}}(.*?)\n{{antonimy}}', re.DOTALL)
	regex['pola-antonimy'] = re.compile(u'{{antonimy}}(.*?)\n({{hiperonimy}}|{{hiponimy}}|{{holonimy}}|{{meronimy}}|{{pokrewne}})', re.DOTALL)
	regex['pola-hiperonimy'] = re.compile(u'{{hiperonimy}}(.*?)\n({{hiponimy}}|{{holonimy}}|{{meronimy}}|{{pokrewne}})', re.DOTALL)
	regex['pola-hiponimy'] = re.compile(u'{{hiponimy}}(.*?)\n({{holonimy}}|{{meronimy}}|{{pokrewne}})', re.DOTALL)
	regex['pola-holonimy'] = re.compile(u'{{holonimy}}(.*?)\n({{meronimy}}|{{pokrewne}})', re.DOTALL)
	regex['pola-meronimy'] = re.compile(u'{{meronimy}}(.*?)\n{{pokrewne}}', re.DOTALL)
	regex['pola-pokrewne'] = re.compile(u'{{pokrewne}}(.*?)\n{{frazeologia}}', re.DOTALL)
	regex['pola-frazeologia'] = re.compile(u'{{frazeologia}}(.*?)\n{{etymologia}}', re.DOTALL)
	regex['pola-etymologia'] = re.compile(u'{{etymologia}}(.*?)\n{{uwagi}}', re.DOTALL)
	regex['pola-uwagi'] = re.compile(u'{{uwagi}}(.*?)\n{{źródła}}', re.DOTALL)
	regex['pola-zrodla'] = re.compile(u'{{źródła}}(.*)', re.DOTALL)
	
	#polish (with translations)
	regex['pola-pl-uwagi'] = re.compile(u'{{uwagi}}(.*?)\n{{tłumaczenia}}', re.DOTALL)
	regex['pola-pl-tlumaczenia'] = re.compile(u'\n{{tłumaczenia}}(.*?)\n{{źródła}}', re.DOTALL)
	
	#japanese words
	regex['pola-ja-kan-dodatki'] = re.compile(ur'(.*?)(\n|){{czytania}}', re.DOTALL)
	regex['pola-ja-kan-czytania'] = re.compile(ur'{{czytania}}(.*?)\n{{wymowa}}', re.DOTALL)
	regex['pola-ja-kan-antonimy'] = re.compile(ur'{{antonimy}}(.*?)\n({{hiperonimy}}|{{hiponimy}}|{{holonimy}}|{{meronimy}}|{{złożenia}})', re.DOTALL)
	regex['pola-ja-kan-hiperonimy'] = re.compile(u'{{hiperonimy}}(.*?)\n({{hiponimy}}|{{holonimy}}|{{meronimy}}|{{złożenia}})', re.DOTALL)
	regex['pola-ja-kan-hiponimy'] = re.compile(u'{{hiponimy}}(.*?)\n({{holonimy}}|{{meronimy}}|{{złożenia}})', re.DOTALL)
	regex['pola-ja-kan-holonimy'] = re.compile(u'{{holonimy}}(.*?)\n({{meronimy}}|{{złożenia}})', re.DOTALL)
	regex['pola-ja-kan-meronimy'] = re.compile(u'{{meronimy}}(.*?)\n{{złożenia}}', re.DOTALL)
	regex['pola-ja-kan-zlozenia'] = re.compile(ur'{{złożenia}}(.*?)\n{{pokrewne}}', re.DOTALL)
	
	#korean kanji words
	regex['pola-ko-zlozenia'] = re.compile(ur'{{złożenia}}(.*?)\n{{pokrewne}}', re.DOTALL)
	
	#kanji (chinese sign section)
	regex['pola-zch-klucz'] = re.compile(ur'{{klucz}}(.*?)\n{{kreski}}', re.DOTALL)
	regex['pola-zch-kreski'] = re.compile(ur'{{kreski}}(.*?)\n{{warianty', re.DOTALL)
	regex['pola-zch-warianty'] = re.compile(ur'{{warianty(\s*?\|.*?)}}\n{{kolejność}}', re.DOTALL)
	regex['pola-zch-kolejnosc'] = re.compile(ur'{{kolejność}}(.*?)\n{{znaczenia}}', re.DOTALL)
	regex['pola-zch-znaczeniaWhole'] = re.compile(ur'{{znaczenia}}(.*?)\n{{etymologia}}', re.DOTALL)
	regex['pola-zch-etymologia'] = re.compile(ur'{{etymologia}}(.*?)\n{{kody', re.DOTALL)
	regex['pola-zch-kody'] = re.compile(ur'{{kody(\s*?\|.*?)}}\n{{słowniki', re.DOTALL)
	regex['pola-zch-slowniki'] = re.compile(ur'{{słowniki(\s*?\|.*?|)}}\n{{uwagi', re.DOTALL)
	
	#esperanto morpheme
	regex['pola-eom-antonimy'] = re.compile(ur'{{antonimy}}(.*?)\n{{pochodne}}', re.DOTALL)
	regex['pola-eom-pochodne'] = re.compile(ur'{{pochodne}}(.*?)\n{{frazeologia}}', re.DOTALL)
	
	#esperanto normal
	regex['pola-eo-dodatki'] = re.compile(ur'(.*?){{morfologia}}', re.DOTALL)
	regex['pola-eo-morfologia'] = re.compile(ur'{{morfologia}}(.*?)\n{{wymowa}}', re.DOTALL)
	
	#chiński standardowy, miękkie przekierowanie do uproszczonego ekwiwalentu
	regex['pola-zh-ekwi'] = re.compile(ur'({{zob-ekwiw-pupr\|.*?}})')
	
	#ancient egyptian
	regex['pola-egy-dodatki'] = re.compile(ur'(.*?){{zapis hieroglificzny}}', re.DOTALL)
	regex['pola-egy-hieroglificzny'] = re.compile(ur'{{zapis hieroglificzny}}(.*?)\n{{transliteracja}}', re.DOTALL)
	regex['pola-egy-transliteracja'] = re.compile(ur'{{transliteracja}}(.*?)\n{{transkrypcja}}', re.DOTALL)
	regex['pola-egy-transkrypcja'] = re.compile(ur'{{transkrypcja}}(.*?)\n{{znaczenia}}', re.DOTALL)
	regex['pola-egy-znaczeniaWhole'] = re.compile(u'{{znaczenia}}(.*?)\n{{determinatywy}}', re.DOTALL)
	regex['pola-egy-determinatywy'] = re.compile(ur'{{determinatywy}}(.*?)\n{{odmiana}}', re.DOTALL)
	
	#others
	regex['pola-nr'] = re.compile(ur'\(([0-9]\.[0-9]\.*[0-9]*)\)')
						
	def __init__(self, text='afeof5imad3sfa5', title = '2o3iremdas', type=666, lang='bumbum'):
                self.sectionOrder = collections.OrderedDict()
                self.sectionOrder['default'] = [subSection(u'wymowa'), subSection(u'znaczenia'), subSection(u'odmiana'), subSection(u'przykłady'), subSection(u'składnia'), subSection(u'kolokacje'), subSection(u'synonimy'), subSection(u'antonimy'), subSection(u'hiperonimy', 1), subSection(u'hiponimy', 1), subSection(u'holonimy', 1), subSection(u'meronimy', 1), subSection(u'pokrewne'), subSection(u'frazeologia'), subSection(u'etymologia'), subSection(u'uwagi'), subSection(u'źródła')]
                self.subSections = collections.OrderedDict()
		if text == 'afeof5imad3sfa5' and title != '2o3iremdas' and type != 666 and lang != 'bumbum':
			self.title = title
			self.langLong = lang
			self.lang = lang.replace(u'język ', u'')
			self.type = type
			if type in (1,9,10,12):
				self.header = u'== %s ({{%s}}) ==' % (title, lang)
				self.dodatki = Pole(u'')
				self.wymowa = Pole(u'')
				self.znaczeniaWhole = Pole(u'')
				self.znaczeniaDetail = []
				self.odmiana = Pole(u'')
				self.przyklady = Pole(u'')
				self.skladnia = Pole(u'')
				self.kolokacje = Pole(u'')
				self.synonimy = Pole(u'')
				self.hiperonimy = Pole(u'')
				self.hiponimy = Pole(u'')
				self.holonimy = Pole(u'')
				self.meronimy = Pole(u'')
				self.antonimy = Pole(u'')
				self.frazeologia = Pole(u'')
				self.etymologia = Pole(u'')
				self.uwagi = Pole(u'')
				self.zrodla = Pole(u'')
			elif type == 4:
				self.lang = u'znak chiński'
				self.header = u'== {{zh|%s}} ({{%s}}) ==' % (title, lang)
				self.klucz = Pole(u'')
				self.kreski = Pole(u'')
				self.warianty = Pole(u'', 'warianty')
				self.kolejnosc = Pole(u'', 'kolejnosc')
				self.znaczeniaWhole = Pole(u'')
				self.etymologia = Pole(u'', 'zch-etym')
				self.kody = Pole(u'', 'kody')
				self.slowniki = Pole(u'', 'slowniki')
				self.uwagi = Pole(u'')
				self.zrodla = Pole(u'')
			else:
				print u'this section type is not available yet'
			if type in (9,12):
				self.pokrewne = Pole(u'')
			if type == 9:
				self.tlumaczenia = Pole(u'')
			if type == 12:
				self.morfologia = Pole(u'')
			if type == 10:
				self.pochodne = Pole(u'')		
				
		elif text != 'afeof5imad3sfa5' and type == 666 and lang == 'bumbum':

			s_lang = re.search(self.regex['init-lang'], text)
			s_langLong = re.search(self.regex['init-langLong'], text)
			s_headerAndContent = re.search(self.regex['init-headerAndContent'], text)
			if s_lang and s_langLong and s_headerAndContent:
				self.title = title
				self.titleHeader = s_lang.group(1)
				if s_lang.group(4):
					self.headerArg = s_lang.group(4)
				else:
					self.headerArg = u''
				self.header = s_headerAndContent.group(1).strip()
				self.lang = s_lang.group(3)
				self.langUpper = self.lang[0].upper() + self.lang[1:]
				self.langLong = s_langLong.group(2)
				self.content = s_headerAndContent.group(2)
				self.type = 1
			else:
				self.type = 2
				raise WrongHeader
	
	def updateHeader(self):
		
		self.header = u'== %s ({{%s' % (self.titleHeader, self.langLong)
		if self.headerArg:
			self.header += u'|%s' % self.headerArg
		self.header += u'}}) =='
	
	def saveChanges(self):
		try: self.znaczeniaDetail
		except AttributeError:
			pass
		else:
			znaczeniaWhole = u''
			for a in self.znaczeniaDetail: # łączy sekcję "znaczenia" (jest wcześniej rozbijana na "część mowy" i znaczenie)
				znaczeniaWhole += u'\n' + a[0] + a[1]
			self.znaczeniaWhole = Pole(znaczeniaWhole)
		
		if self.type == 9:
			self.content = self.dodatki.text + u'\n{{wymowa}}' + self.wymowa.text + u'\n{{znaczenia}}' + self.znaczeniaWhole.text + u'\n{{odmiana}}' + self.odmiana.text + u'\n{{przykłady}}' + self.przyklady.text + u'\n{{składnia}}' + self.skladnia.text + u'\n{{kolokacje}}' + self.kolokacje.text + u'\n{{synonimy}}' + self.synonimy.text + u'\n{{antonimy}}' + self.antonimy.text + u'\n{{hiperonimy}}' + self.hiperonimy.text + u'\n{{hiponimy}}' + self.hiponimy.text + u'\n{{holonimy}}' + self.holonimy.text + u'\n{{meronimy}}' + self.meronimy.text + u'\n{{pokrewne}}' + self.pokrewne.text + u'\n{{frazeologia}}' + self.frazeologia.text + u'\n{{etymologia}}' + self.etymologia.text + u'\n{{uwagi}}' + self.uwagi.text + u'\n{{tłumaczenia}}' + self.tlumaczenia.text + u'\n{{źródła}}' + self.zrodla.text
		elif self.type == 8:
			self.content = self.dodatki.text + u'\n{{wymowa}}' + self.wymowa.text + u'\n{{znaczenia}}' + self.znaczeniaWhole.text + u'\n{{przykłady}}' + self.przyklady.text + u'\n{{złożenia}}' + self.zlozenia.text + u'\n{{etymologia}}' + self.etymologia.text + u'\n{{uwagi}}' + self.uwagi.text + u'\n{{źródła}}' + self.zrodla.text
		elif self.type == 6:
			self.content = self.dodatki.text + u'\n{{czytania}}' + self.czytania.text + u'\n{{wymowa}}' + self.wymowa.text + u'\n{{znaczenia}}' + self.znaczeniaWhole.text + u'\n{{odmiana}}' + self.odmiana.text + u'\n{{przykłady}}' + self.przyklady.text + u'\n{{składnia}}' + self.skladnia.text + u'\n{{kolokacje}}' + self.kolokacje.text + u'\n{{synonimy}}' + self.synonimy.text + u'\n{{antonimy}}' + self.antonimy.text + u'\n{{złożenia}}' + self.zlozenia.text + u'\n{{pokrewne}}' + self.pokrewne.text + u'\n{{frazeologia}}' + self.frazeologia.text + u'\n{{etymologia}}' + self.etymologia.text + u'\n{{uwagi}}' + self.uwagi.text + u'\n{{źródła}}' + self.zrodla.text
		elif self.type == 4:
			self.content = u'\n{{klucz}}' + self.klucz.text + u'\n{{kreski}}' + self.kreski.text + u'\n{{warianty' + self.warianty.merge(2) + u'}}' + u'\n{{kolejność}}' + self.kolejnosc.merge(2) + u'\n{{znaczenia}}' + self.znaczeniaWhole.text + u'\n{{etymologia}}' + self.etymologia.merge(2) + u'\n{{kody' + self.kody.merge(2) + u'}}' + u'\n{{słowniki' + self.slowniki.merge(2) + u'}}' + u'\n{{uwagi}}' + self.uwagi.text + u'\n{{źródła}}' + self.zrodla.text
		elif self.type == 1:
			self.content = self.dodatki.text + u'\n{{wymowa}}' + self.wymowa.text + u'\n{{znaczenia}}' + self.znaczeniaWhole.text + u'\n{{odmiana}}' + self.odmiana.text + u'\n{{przykłady}}' + self.przyklady.text + u'\n{{składnia}}' + self.skladnia.text + u'\n{{kolokacje}}' + self.kolokacje.text + u'\n{{synonimy}}' + self.synonimy.text + u'\n{{antonimy}}' + u'\n{{hiperonimy}}' + self.hiperonimy.text + u'\n{{hiponimy}}' + self.hiponimy.text + u'\n{{holonimy}}' + self.holonimy.text + u'\n{{meronimy}}' + self.meronimy.text + self.antonimy.text + u'\n{{pokrewne}}' + self.pokrewne.text + u'\n{{frazeologia}}' + self.frazeologia.text + u'\n{{etymologia}}' + self.etymologia.text + u'\n{{uwagi}}' + self.uwagi.text + u'\n{{źródła}}' + self.zrodla.text
		elif self.type == 10:
			self.content = self.dodatki.text + u'\n{{wymowa}}' + self.wymowa.text + u'\n{{znaczenia}}' + self.znaczeniaWhole.text + u'\n{{odmiana}}' + self.odmiana.text + u'\n{{przykłady}}' + self.przyklady.text + u'\n{{składnia}}' + self.skladnia.text + u'\n{{kolokacje}}' + self.kolokacje.text + u'\n{{synonimy}}' + self.synonimy.text + u'\n{{antonimy}}' + self.antonimy.text + u'\n{{pochodne}}' + self.pochodne.text + u'\n{{frazeologia}}' + self.frazeologia.text + u'\n{{etymologia}}' + self.etymologia.text + u'\n{{uwagi}}' + self.uwagi.text + u'\n{{źródła}}' + self.zrodla.text	
		
	def pola(self):
		specialLangs = (u'japoński', u'koreański')
		if self.type == 1:
			s_zrodla = re.search(self.regex['pola-zrodla'], self.content)
			if s_zrodla:
				self.zrodla = Pole(s_zrodla.group(1))

				if self.lang == u'znak chiński':
					s_klucz_zch = re.search(self.regex['pola-zch-klucz'], self.content)
					s_kreski_zch = re.search(self.regex['pola-zch-kreski'], self.content)
					s_warianty_zch = re.search(self.regex['pola-zch-warianty'], self.content)
					s_kolejnosc_zch = re.search(self.regex['pola-zch-kolejnosc'], self.content)
					s_znaczeniaWhole_zch = re.search(self.regex['pola-zch-znaczeniaWhole'], self.content)
					s_etymologia_zch = re.search(self.regex['pola-zch-etymologia'], self.content)
					s_kody_zch = re.search(self.regex['pola-zch-kody'], self.content)
					s_slowniki_zch = re.search(self.regex['pola-zch-slowniki'], self.content)
					s_uwagi = re.search(self.regex['pola-uwagi'], self.content)
					
					if s_klucz_zch and s_kreski_zch and s_warianty_zch and s_kolejnosc_zch and s_znaczeniaWhole_zch and s_etymologia_zch and s_kody_zch and s_slowniki_zch:
						self.type = 4
						self.klucz = Pole(s_klucz_zch.group(1))
						self.kreski = Pole(s_kreski_zch.group(1))
						self.warianty = Pole(s_warianty_zch.group(1), u'warianty')
						self.kolejnosc = Pole(s_kolejnosc_zch.group(1), u'kolejnosc')
						self.znaczeniaWhole = Pole(s_znaczeniaWhole_zch.group(1))
						self.etymologia = Pole(s_etymologia_zch.group(1), u'zch-etym')
						self.kody = Pole(s_kody_zch.group(1), u'kody')
						self.slowniki = Pole(s_slowniki_zch.group(1), u'slowniki')
						self.uwagi = Pole(s_uwagi.group(1))
					else:
						self.type = 7
				elif self.lang == u'staroegipski':
					s_dodatki_egyp = re.search(self.regex['pola-egy-dodatki'], self.content)
					s_zapis_hieroglificzny = re.search(self.regex['pola-egy-hieroglificzny'], self.content)
					s_transkrypcja_egyp = re.search(self.regex['pola-egy-transkrypcja'], self.content)
					s_transliteracja_egyp = re.search(self.regex['pola-egy-transliteracja'], self.content)
					s_znaczeniaWhole_egyp = re.search(self.regex['pola-egy-znaczeniaWhole'], self.content)
					s_determinatywy = re.search(self.regex['pola-egy-determinatywy'], self.content)
	
					s_odmiana = re.search(self.regex['pola-odmiana'], self.content)				
					s_przyklady = re.search(self.regex['pola-przyklady'], self.content)
					s_skladnia = re.search(self.regex['pola-skladnia'], self.content)
					s_kolokacje = re.search(self.regex['pola-kolokacje'], self.content)
					s_synonimy = re.search(self.regex['pola-synonimy'], self.content)
					s_antonimy = re.search(self.regex['pola-antonimy'], self.content)
					s_hiperonimy = re.search(self.regex['pola-hiperonimy'], self.content)
					s_hiponimy = re.search(self.regex['pola-hiponimy'], self.content)
					s_holonimy = re.search(self.regex['pola-holonimy'], self.content)
					s_meronimy = re.search(self.regex['pola-meronimy'], self.content)
					s_pokrewne = re.search(self.regex['pola-pokrewne'], self.content)
					s_frazeologia = re.search(self.regex['pola-frazeologia'], self.content)
					s_etymologia = re.search(self.regex['pola-etymologia'], self.content)
					s_uwagi = re.search(self.regex['pola-uwagi'], self.content)
					s_zrodla = re.search(self.regex['pola-zrodla'], self.content)
					
					if s_dodatki_egyp and s_zapis_hieroglificzny and s_transliteracja_egyp and s_transkrypcja_egyp and s_znaczeniaWhole_egyp and s_determinatywy and s_odmiana and s_przyklady and s_skladnia and s_kolokacje and s_synonimy and s_antonimy and s_pokrewne and s_frazeologia and s_etymologia and s_uwagi:
						self.type = 13
						self.dodatki = Pole(s_dodatki_egyp.group(1))
						self.zapisHieroglificzny = Pole(s_zapis_hieroglificzny.group(1))
						self.transliteracja = Pole(s_transliteracja_egyp.group(1))
						self.transkrypcja = Pole(s_transkrypcja_egyp.group(1))
						self.znaczeniaWhole = Pole(s_znaczeniaWhole_egyp.group(1))
						self.determinatywy = Pole(s_determinatywy.group(1))
						self.odmiana = Pole(s_odmiana.group(1))
						self.przyklady = Pole(s_przyklady.group(1))
						self.skladnia = Pole(s_skladnia.group(1))
						self.kolokacje = Pole(s_kolokacje.group(1))
						self.synonimy = Pole(s_synonimy.group(1))
						self.antonimy = Pole(s_antonimy.group(1))
						if s_hiperonimy:
							self.hiperonimy = Pole(s_hiperonimy.group(1))
						else:
							self.hiperonimy = Pole(u'')
						if s_hiponimy:
							self.hiponimy = Pole(s_hiponimy.group(1))
						else:
							self.hiponimy = Pole(u'')
						if s_holonimy:
							self.holonimy = Pole(s_holonimy.group(1))
						else:
							self.holonimy = Pole(u'')
						if s_meronimy:
							self.meronimy = Pole(s_meronimy.group(1))
						else:
							self.meronimy = Pole(u'')
						self.pokrewne = Pole(s_pokrewne.group(1))
						self.frazeologia = Pole(s_frazeologia.group(1))
						self.etymologia = Pole(s_etymologia.group(1))
						self.uwagi = Pole(s_uwagi.group(1))
					else:
						self.type = 7
				
				elif u'esperanto' in self.lang:

					s_dodatki = re.search(self.regex['pola-dodatki'], self.content)
					s_wymowa = re.search(self.regex['pola-wymowa'], self.content)
					s_znaczeniaWhole = re.search(self.regex['pola-znaczeniaWhole'], self.content)
					s_odmiana = re.search(self.regex['pola-odmiana'], self.content)
					s_przyklady = re.search(self.regex['pola-przyklady'], self.content)
					s_skladnia = re.search(self.regex['pola-skladnia'], self.content)
					s_kolokacje = re.search(self.regex['pola-kolokacje'], self.content)
					s_synonimy = re.search(self.regex['pola-synonimy'], self.content)
					s_antonimy = re.search(self.regex['pola-antonimy'], self.content)
					s_hiperonimy = re.search(self.regex['pola-hiperonimy'], self.content)
					s_hiponimy = re.search(self.regex['pola-hiponimy'], self.content)
					s_holonimy = re.search(self.regex['pola-holonimy'], self.content)
					s_meronimy = re.search(self.regex['pola-meronimy'], self.content)
					s_pokrewne = re.search(self.regex['pola-pokrewne'], self.content)
					s_frazeologia = re.search(self.regex['pola-frazeologia'], self.content)
					s_etymologia = re.search(self.regex['pola-etymologia'], self.content)
					s_uwagi = re.search(self.regex['pola-uwagi'], self.content)
					
					if s_wymowa and s_znaczeniaWhole and s_odmiana and s_przyklady and s_skladnia and s_kolokacje and s_synonimy and s_frazeologia and s_etymologia and s_uwagi:
						self.wymowa = Pole(s_wymowa.group(1))
						self.znaczeniaWhole = Pole(s_znaczeniaWhole.group(1))
						self.odmiana = Pole(s_odmiana.group(1))
						self.przyklady = Pole(s_przyklady.group(1))
						self.skladnia = Pole(s_skladnia.group(1))
						self.kolokacje = Pole(s_kolokacje.group(1))
						self.synonimy = Pole(s_synonimy.group(1))
						if s_hiperonimy:
							self.hiperonimy = Pole(s_hiperonimy.group(1))
						else:
							self.hiperonimy = Pole(u'')
						if s_hiponimy:
							self.hiponimy = Pole(s_hiponimy.group(1))
						else:
							self.hiponimy = Pole(u'')
						if s_holonimy:
							self.holonimy = Pole(s_holonimy.group(1))
						else:
							self.holonimy = Pole(u'')
						if s_meronimy:
							self.meronimy = Pole(s_meronimy.group(1))
						else:
							self.meronimy = Pole(u'')
						self.frazeologia = Pole(s_frazeologia.group(1))
						self.etymologia = Pole(s_etymologia.group(1))
						self.uwagi = Pole(s_uwagi.group(1))

						if u'(morfem)' in self.lang:
							s_antonimy_eom = re.search(self.regex['pola-eom-antonimy'], self.content)
							s_pochodne_eom = re.search(self.regex['pola-eom-pochodne'], self.content)
							if s_antonimy_eom and s_pochodne_eom:
								self.type = 10
								self.dodatki = Pole(s_dodatki.group(1))
								self.antonimy = Pole(s_antonimy_eom.group(1))
								self.pochodne = Pole(s_pochodne_eom.group(1))
							else:
								self.type = 7
						else:
							s_dodatki_eo = re.search(self.regex['pola-eo-dodatki'], self.content)
							s_morfologia_eo = re.search(self.regex['pola-eo-morfologia'], self.content)
							s_antonimy = re.search(self.regex['pola-antonimy'], self.content)
							s_pokrewne = re.search(self.regex['pola-pokrewne'], self.content)
						
							if s_dodatki_eo and s_morfologia_eo:
								self.type = 12
								self.morfologia = Pole(s_morfologia_eo.group(1))
								self.dodatki = Pole(s_dodatki_eo.group(1))							
								self.antonimy = Pole(s_antonimy.group(1))
								self.pokrewne = Pole(s_pokrewne.group(1))
							else:
								self.type = 7
					else:
						self.type = 7
				elif self.lang == u'japoński' or self.lang == u'koreański':
					
					
					s_zlozenia_kanji = re.search(self.regex['pola-ja-kan-zlozenia'], self.content)
					s_antonimy_kanji = re.search(self.regex['pola-ja-kan-antonimy'], self.content)
					s_hiperonimy_kanji = re.search(self.regex['pola-ja-kan-hiperonimy'], self.content)
					s_hiponimy_kanji = re.search(self.regex['pola-ja-kan-hiponimy'], self.content)
					s_holonimy_kanji = re.search(self.regex['pola-ja-kan-holonimy'], self.content)
					s_meronimy_kanji = re.search(self.regex['pola-ja-kan-meronimy'], self.content)
					
					s_wymowa = re.search(self.regex['pola-wymowa'], self.content)
					s_znaczeniaWhole = re.search(self.regex['pola-znaczeniaWhole'], self.content)
					s_odmiana = re.search(self.regex['pola-odmiana'], self.content)
					s_przyklady = re.search(self.regex['pola-przyklady'], self.content)
					s_skladnia = re.search(self.regex['pola-skladnia'], self.content)
					s_kolokacje = re.search(self.regex['pola-kolokacje'], self.content)
					s_synonimy = re.search(self.regex['pola-synonimy'], self.content)
					s_pokrewne = re.search(self.regex['pola-pokrewne'], self.content)
					s_frazeologia = re.search(self.regex['pola-frazeologia'], self.content)
					s_etymologia = re.search(self.regex['pola-etymologia'], self.content)
					s_uwagi = re.search(self.regex['pola-uwagi'], self.content)
					
					if s_wymowa and s_znaczeniaWhole and s_odmiana and s_przyklady and s_skladnia and s_kolokacje and s_synonimy and s_pokrewne and s_etymologia and s_uwagi and s_zlozenia_kanji and s_antonimy_kanji:
						self.wymowa = Pole(s_wymowa.group(1))
						self.znaczeniaWhole = Pole(s_znaczeniaWhole.group(1))
						self.odmiana = Pole(s_odmiana.group(1))
						self.przyklady = Pole(s_przyklady.group(1))
						self.skladnia = Pole(s_skladnia.group(1))
						self.kolokacje = Pole(s_kolokacje.group(1))
						self.synonimy = Pole(s_synonimy.group(1))
						self.antonimy = Pole(s_antonimy_kanji.group(1))
						if s_hiperonimy_kanji:
							self.hiperonimy = Pole(s_hiperonimy_kanji.group(1))
						else:
							self.hiperonimy = Pole(u'')
						if s_hiponimy_kanji:
							self.hiponimy = Pole(s_hiponimy_kanji.group(1))
						else:
							self.hiponimy = Pole(u'')
						if s_holonimy_kanji:
							self.holonimy = Pole(s_holonimy_kanji.group(1))
						else:
							self.holonimy = Pole(u'')
						if s_meronimy_kanji:
							self.meronimy = Pole(s_meronimy_kanji.group(1))
						else:
							self.meronimy = Pole(u'')
						self.zlozenia = Pole(s_zlozenia_kanji.group(1))
						self.pokrewne = Pole(s_pokrewne.group(1))
						self.frazeologia = Pole(s_frazeologia.group(1))
						self.etymologia = Pole(s_etymologia.group(1))
						self.uwagi = Pole(s_uwagi.group(1))
						
						if self.lang == u'japoński':
							s_dodatki_kanji = re.search(self.regex['pola-ja-kan-dodatki'], self.content)
							s_czytania_kanji = re.search(self.regex['pola-ja-kan-czytania'], self.content)
							
							if s_dodatki_kanji and s_czytania_kanji:
								self.type = 6
								self.dodatki = Pole(s_dodatki_kanji.group(1))
								self.czytania = Pole(s_czytania_kanji.group(1))
							else:
								self.type = 7
						else:
							s_dodatki = re.search(self.regex['pola-dodatki'], self.content)
							
							if s_dodatki:
								self.type = 8
								self.dodatki = Pole(s_dodatki.group(1))
							else:
								self.type = 7
					else:
						self.type = 7
				else:
                                    for i, subsect in enumerate(self.sectionOrder['default']):
                                        if i == 0:
                                            reg = re.compile(ur'(.*?)(\n|){{%s}}' % (self.sectionOrder['default'][0].name), re.DOTALL)
                                        elif i == len(self.sectionOrder['default']) -1:
                                            reg = re.compile(ur'{{%s}}(.*)' % (self.sectionOrder['default'][i].name), re.DOTALL)
                                        else:
                                            reg = re.compile(ur'{{%s}}(.*?){{%s}}' % (self.sectionOrder['default'][i].name, self.sectionOrder['default'][i+1].name) , re.DOTALL)

                                        s = re.search(reg, self.content)
                                        if s:
                                            print s.group(1)
                                            self.subSections[subsect.name] = Pole(s.group(1))
                                        elif self.sectionOrder['default'][i].optional == 1:
                                            self.subSections[subsect.name] = Pole(u'')
                                    
                                    for elem in self.subSections:
                                        print u'----- %s -----' % elem
                                        print self.subSections[elem].text
                                    
                                    s_dodatki = re.search(self.regex['pola-dodatki'], self.content)
                                    s_wymowa = re.search(self.regex['pola-wymowa'], self.content)
                                    s_znaczeniaWhole = re.search(self.regex['pola-znaczeniaWhole'], self.content)
                                    s_odmiana = re.search(self.regex['pola-odmiana'], self.content)
                                    s_przyklady = re.search(self.regex['pola-przyklady'], self.content)
                                    s_skladnia = re.search(self.regex['pola-skladnia'], self.content)
                                    s_kolokacje = re.search(self.regex['pola-kolokacje'], self.content)
                                    s_synonimy = re.search(self.regex['pola-synonimy'], self.content)
                                    s_antonimy = re.search(self.regex['pola-antonimy'], self.content)
                                    s_hiperonimy = re.search(self.regex['pola-hiperonimy'], self.content)
                                    s_hiponimy = re.search(self.regex['pola-hiponimy'], self.content)
                                    s_holonimy = re.search(self.regex['pola-holonimy'], self.content)
                                    s_meronimy = re.search(self.regex['pola-meronimy'], self.content)
                                    s_pokrewne = re.search(self.regex['pola-pokrewne'], self.content)
                                    s_frazeologia = re.search(self.regex['pola-frazeologia'], self.content)
                                    s_etymologia = re.search(self.regex['pola-etymologia'], self.content)

                                    if s_wymowa and s_znaczeniaWhole and s_dodatki and s_odmiana and s_przyklady and s_skladnia and s_kolokacje and s_synonimy and s_antonimy and s_pokrewne and s_frazeologia and s_etymologia:
                                            self.dodatki = Pole(s_dodatki.group(1))
                                            self.wymowa = Pole(s_wymowa.group(1))
                                            self.znaczeniaWhole = Pole(s_znaczeniaWhole.group(1))
                                            self.odmiana = Pole(s_odmiana.group(1))
                                            self.przyklady = Pole(s_przyklady.group(1))
                                            self.skladnia = Pole(s_skladnia.group(1))
                                            self.kolokacje = Pole(s_kolokacje.group(1))
                                            self.synonimy = Pole(s_synonimy.group(1))
                                            self.antonimy = Pole(s_antonimy.group(1))
                                            if s_hiperonimy:
                                                    self.hiperonimy = Pole(s_hiperonimy.group(1))
                                            else:
                                                    self.hiperonimy = Pole(u'')
                                            if s_hiponimy:
                                                    self.hiponimy = Pole(s_hiponimy.group(1))
                                            else:
                                                    self.hiponimy = Pole(u'')
                                            if s_holonimy:
                                                    self.holonimy = Pole(s_holonimy.group(1))
                                            else:
                                                    self.holonimy = Pole(u'')
                                            if s_meronimy:
                                                    self.meronimy = Pole(s_meronimy.group(1))
                                            else:
                                                    self.meronimy = Pole(u'')
                                            self.pokrewne = Pole(s_pokrewne.group(1))
                                            self.frazeologia = Pole(s_frazeologia.group(1))
                                            self.etymologia = Pole(s_etymologia.group(1))

                                            if self.lang == u'polski':
                                                    s_uwagi_pl = re.search(self.regex['pola-pl-uwagi'], self.content)
                                                    s_tlumaczenia = re.search(self.regex['pola-pl-tlumaczenia'], self.content)
                                                    if s_uwagi_pl and s_tlumaczenia:
                                                            self.type = 9
                                                            self.uwagi = Pole(s_uwagi_pl.group(1))
                                                            self.tlumaczenia = Pole(s_tlumaczenia.group(1))
                                                    else:
                                                            self.type = 7
                                            else:
                                                    s_uwagi = re.search(self.regex['pola-uwagi'], self.content)
                                                    if s_uwagi:
                                                            self.uwagi = Pole(s_uwagi.group(1))
                                                    else:
                                                            self.type = 7				
                                    else:
                                            self.type = 7
			else:
				self.type = 2
				'''	
				elif self.lang == u'chiński standardowy':
					s_ekwi_zh = re.search(self.regex['pola-zh-ekwi'], self.content)
				
	
				elif self.lang == u'chiński standardowy' and s_ekwi_zh and not s_wymowa and not s_przyklady and not s_odmiana and not s_zrodla and not s_etymologia:
					self.type = 11
					self.dodatki = Pole(s_ekwi_zh.group(1))'''
				
				
			if self.type not in (2,3,7,11):
				s_znaczeniaDetail = re.findall(self.regex['pola-znaczeniaDetail'], self.znaczeniaWhole.text)
				if s_znaczeniaDetail:
					self.znaczeniaDetail = [list(tup) for tup in s_znaczeniaDetail]
					# checking if the last number [(1.1), (2.1) etc.] matches the length of self.znaczeniaDetail - if it doesn't, it means that the numbering is invalid
					s_numer = re.search(self.regex['pola-nr'], self.znaczeniaDetail[-1][1])
					if int(s_numer.group(1)[0]) != len(self.znaczeniaDetail):
						self.type = 14
				else:
					if self.type == 4:
						self.znaczeniaDetail = []
					else:
						self.type = 5
				
			
		
class Pole():
	regex = {}
	regex['init-warianty-details'] = re.compile(ur'{{zch-w\|([a-z]*?)\|(.*?)}}')
	regex['init-obrazek'] = re.compile(ur'{{zch-obrazek\|([a-z]*?)\|(.*?)}}')
	regex['init-kodySlowniki-details'] = re.compile(ur'([a-z]*?)=(.*?)(?=\||$)')
	regex['init-kolejnosc'] = re.compile(ur'({{zch-komiks|{{zch-animacja|{{zch-cienie)[\|]*(.*?)}}')
	regex['numer-nr-whole'] = re.compile(ur'(\:\s*?\([1-9].*?\))(.*?)(?=\n\:|$)', re.DOTALL)
	
	def __init__(self, text, type='auto'):

		self.type = type
		self.text = text
		self.list = []
		self.dict = {}
		if type == u'warianty':
			warianty = re.findall(self.regex['init-warianty-details'], self.text)
			for b in warianty:
				if not self.dict.has_key(b[0]):
					self.dict[b[0]] = []
				self.dict[b[0]].append(b[1])
			warianty_obrazek = re.findall(self.regex['init-obrazek'], self.text)
			for b in warianty_obrazek:
				self.dict[b[0]] = b[1]
		if type == u'zch-etym':
			etymologia = re.findall(self.regex['init-obrazek'], self.text)
			for b in etymologia:
				self.dict[b[0]] = b[1]
		if type == u'kolejnosc':
			kolejnosc = re.findall(self.regex['init-kolejnosc'], self.text)
			for b in kolejnosc:
				self.dict[b[1]] = b[0]
		if type == u'kody' or type == u'slowniki':
			kody = re.findall(self.regex['init-kodySlowniki-details'], self.text)
			for b in kody:
				self.dict[b[0]] = b[1]
	def merge(self, mode=2): #mode = 1 - test for a proper field, return 0 if invalid; mode=2 - merge a list/dict into a string
		text=u''
		if self.type == u'warianty':
			text = u' |'
			if self.dict.has_key(u'ct'):
				for a in self.dict[u'ct']:
					text += u' {{zch-w|ct|%s}} |' % a
			if self.dict.has_key(u'cu'):
				for a in self.dict[u'cu']:
					text += u' {{zch-w|cu|%s}} |' % a
			if self.dict.has_key(u'js'):
				for a in self.dict[u'js']:
					text += u' {{zch-w|js|%s}} |' % a
			if text[-2:] == u' |':
				text = text[:-2]
			if text == u'':
				text += u'|{{zch-w}}'
			if self.dict.has_key(u'c') or self.dict.has_key(u'xt') or self.dict.has_key(u'ca') or self.dict.has_key(u'kt') or self.dict.has_key(u'sot'):
				text += u'}} {{warianty-obrazek |'
			if self.dict.has_key(u'c'):
				text += u' {{zch-obrazek|c|%s}} |' % self.dict[u'c']
			if self.dict.has_key(u'xt'):
				text += u' {{zch-obrazek|xt|%s}} |' % self.dict[u'xt']
			if self.dict.has_key(u'ca'):
				text += u' {{zch-obrazek|ca|%s}} |' % self.dict[u'ca']
			if self.dict.has_key(u'kt'):
				text += u' {{zch-obrazek|kt|%s}} |' % self.dict[u'kt']
			if self.dict.has_key(u'sot'):
				text += u' {{zch-obrazek|sot|%s}} |' % self.dict[u'sot']
			if text[-2:] == u' |':
				text = text[:-2]
		if self.type == u'zch-etym':
			if self.dict.has_key('o') or self.dict.has_key('br') or self.dict.has_key('bs') or self.dict.has_key('ss'):
				text += u' {{warianty-obrazek |'
			if self.dict.has_key('o'):
				text += u' {{zch-obrazek|o|%s}} |' % self.dict[u'o']
			if self.dict.has_key('br'):
				text += u' {{zch-obrazek|br|%s}} |' % self.dict[u'br']
			if self.dict.has_key('bs'):
				text += u' {{zch-obrazek|bs|%s}} |' % self.dict[u'bs']
			if self.dict.has_key('ss'):
				text += u' {{zch-obrazek|ss|%s}} |' % self.dict[u'ss']
			if text[-2:] == u' |':
				text = text[:-2]
			if text:
				text += '}}'
		if self.type == u'kolejnosc':
			if self.dict.has_key(u''):
				text += u'%s}}' % self.dict[u'']
			if self.dict.has_key(u'j'):
				text += u' %s|j}}' % self.dict[u'j']
			if self.dict.has_key(u't'):
				text += u' %s|t}}' % self.dict[u't']
			if self.dict.has_key(u'a'):
				text += u' %s|a}}' % self.dict[u'a']
			text.strip()
			if text:
				text = u'\n' + text
		if self.type == u'kody':
			if self.dict.has_key(u'cjz'):
				text += u'|cjz=%s' % self.dict[u'cjz']
			if self.dict.has_key(u'cr'):
				text += u'|cr=%s' % self.dict[u'cr']
			if self.dict.has_key(u'u'):
				text += u'|u=%s' % self.dict[u'u']
		if self.type == u'slowniki':
			if self.dict.has_key(u'kx'):
				text += u'|kx=%s' % self.dict[u'kx']
			if self.dict.has_key(u'dkj'):
				text += u'|dkj=%s' % self.dict[u'dkj']
			if self.dict.has_key(u'dj'):
				text += u'|dj=%s' % self.dict[u'dj']
			if self.dict.has_key(u'hdz'):
				text += u'|hdz=%s' % self.dict[u'hdz']
		if mode == 1:
			if text != self.text:
				return 0
			else:
				return 1
		else:
			self.text = text
			return text
	def numer(self):
		s_nr_whole = re.findall(self.regex['numer-nr-whole'], self.text)
		testString = u''
		if s_nr_whole:
			self.list = [list(tup) for tup in s_nr_whole]
			for elem in self.list:
				for e in elem:
					testString += e
			if testString.strip().replace(u'\n', u'') != self.text.strip().replace(u'\n', u''):
				self.type = 3
			else:
				self.type = 2
		else:
			self.type = 1
def ReadList(filename):
	list = []
	inp = codecs.open('%s' % filename, encoding='utf-8')
	for line in inp:
		list.append(line.split(u'\n'))
	return list

def flagLastRev(site, revid, comment=u''):
	
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
	page = pywikibot.Page(site, u'Mediawiki:Common.js')
	
	langTable = []
	re_langs = re.compile(ur'function om\$initLangDictionaries\(\) \{\n\tom\$Lang2Code={\n(.*?)\n\t\};', re.DOTALL)
	re_oneLang = re.compile(ur'\s*?"(.*?)"\s*?\:\s*"([a-z-]*?)"')
	
	s_langs = re.search(re_langs, page.get())

	shortOnly = [u'interlingua', u'jidysz', u'ido', u'esperanto', u'esperanto (morfem)', u'slovio', u'tetum', u'hindi', u'użycie międzynarodowe', u'znak chiński', u'volapük', u'inuktitut', u'tok pisin', u'ladino', u'sanskryt', u'tupinambá', u'lojban', u'novial', u'papiamento', u'ewe', u'lingala', u'pitjantjatjara', u'dżuhuri', u'sranan tongo', u'termin obcy w języku polskim', u'quenya', u'brithenig', u'Lingua Franca Nova', u'wenedyk', u'romániço', u'jèrriais']

	if s_langs:
		tempLangTable = re.findall(re_oneLang, s_langs.group(1))
		for a in tempLangTable:
			if a[0] in shortOnly:
				tempLong = a[0]
			else:
				tempLong = u'język %s' % (a[0])
				
			langUpper = a[0][0].upper() + a[0][1:]
			
			langTable.append(Language(a[0], tempLong, langUpper, a[1]))
	else:
		print u'Couldn\'t get languages list!'
		langTable = None
		
	return langTable

def obrazkiAndrzeja():
	#wyniki działania funkcji to dictionary w formie dict['slowo'] = [grafika1, grafika2, ...]
	site = pywikibot.Site()
	pageImages = pywikibot.Page(site, u'Wikipedysta:Andrzej 22/Ilustracje')
	re_sekcja = re.compile(ur'\=\=\s*\[\[(.*?)\]\]\s*\=\=(.*?)(?=\=\=)', re.DOTALL)
	re_img = re.compile(ur'(\[\[Plik\:.*?\]\])(?=\[\[Plik|<br)')
	re_subnr = ws = re.compile(ur'\([0-9]\.[0-9]\)') # do zamieniania (1.1) na {{brak|numer}} w obrazkach
	pageText = pageImages.get()
	s_sekcja = re.findall(re_sekcja, pageText)
	result = collections.defaultdict()
	if s_sekcja:
		for a in s_sekcja:
			s_img = re.findall(re_img, a[1])
			if s_img and a[0]:
				result[a[0]] = []
				for b in s_img:
					b = re.sub(re_subnr, u'{{brak|numer}}', b)
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
		re_lang = re.compile(u'==(| )?{{=(.*?)=}}')
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
			re_etymology = re.compile(u'{{-étym-}}\n(.*?){{-|$', re.DOTALL)
			re_variants = re.compile(u'{{-var-ortho-}}\n(.*?){{-|$', re.DOTALL)
			re_synonyms = re.compile(u'{{-syn-}}\n(.*?){{-|$', re.DOTALL)
			re_antonyms = re.compile(u'{{-ant-}}\n(.*?){{-|$', re.DOTALL)
			re_derives = re.compile(u'{{-drv-}}\n(.*?){{-|$', re.DOTALL)
			re_expressions = re.compile(u'{{-exp-}}\n(.*?){{-|$', re.DOTALL)
			re_translations = re.compile(u'{{-trad-}}\n(.*?){{-|$', re.DOTALL)
			re_pronunciation = re.compile(u'{{-pron-}}\n(.*?){{-|$', re.DOTALL)
			re_noun = re.compile(u'{{-nom-\|(.*?){{-|$', re.DOTALL)
			
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
		
		if u'{{m}}' in self.noun.tresc:
			self.genre = u'm'
		elif u'{{f}}' in self.noun.tresc:
			self.genre = u'f'
		elif u'{{mf}}' in self.noun.tresc:
			self.genre = u'mf'
		elif u'{{mf?}}' in self.noun.tresc:
			self.genre = u'mf?'
		else:
			self.genre = u'unknown'

def pageCounter(language):
	#returns number of entries for a language
	params = {
			'action'	:'expandtemplates',
			'text'		:'{{PAGESINCAT:%s (indeks)|R}}' % language,
			}
	req = Request(**params)
	qr = req.submit()
	print qr['expandtemplates']['*']
		
def RecentChanges(limit):
	limitString = limit
	time_format = "%Y-%m-%dT%H:%M:%SZ"
	limit = datetime.datetime.fromtimestamp(time.mktime(time.strptime(limitString, time_format)))	
	current = datetime.datetime.now()
	list = set()
	params = {
	        'action'    :'query',
	        'list'		:'recentchanges',
			'rcprop'	:'timestamp|title',
			'rclimit'	:'100',
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
	
	file = open(u'%srclimits/%s.txt' % (config.path['scripts'], name), 'w')
	file.write(limit.encode( "utf-8" ))
	file.close
def readRCLimit(name):
	file = open(u'%srclimits/%s.txt' % (config.path['scripts'], name), 'r')
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

def getListFromXML(data, findLatest=False):
	#converts a wikimedia dump to a python list
    #if findLatest True, it will search for the newest dump in dumps folder

    filename = config.path['dumps'] + '%s/plwiktionary-%s-pages-articles.xml.bz2' % (data,data)
    
    if findLatest:
		now = datetime.datetime.now()
		today_year = now.year
		checked = now
		found = 0

		while checked > (now - datetime.timedelta(days=90)):
			if found == 1:
				break
			
			tempDate = checked.strftime('%Y%m%d')
			tempFilename = config.path['dumps'] + tempDate
			
			checked = checked - datetime.timedelta(days=1) #checking day by day
			
			if os.path.isdir(tempFilename):
				found = 1
		
		if found:
			filename = tempFilename + '/plwiktionary-%s-pages-articles.xml.bz2' % (tempDate)
		else:
			raise DumpNotFound
	

    generator = xmlreader.XmlDump.parse(xmlreader.XmlDump(filename))
    return generator
    
    #return list(lista_stron)

def log(text, filename='log_all', test_mode=0):
    if test_mode == 1:
        print text
    else:
        if text != u'':
            file = open("%slog/%s.txt" % (config.path['scripts'], filename), 'a')
            file.write (('\n' + text).encode("utf-8"))
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
		re_lang = re.compile(u'(==\s*?{{=.*?=}}\s*?==\n.*?)$|==', re.DOTALL)
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
		re_lang = re.compile(u'(==\s*?{{=.*?=}}\s*?==\n.*?)$|==', re.DOTALL)
		s_lang = re.findall(re_lang, self.content)
		for b in s_lang:
			self.list_lang.append(SectionFr(b, self.title))	
		else:
			self.type = 4

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
