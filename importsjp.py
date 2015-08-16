#!/usr/bin/python
# -*- coding: iso-8859-2 -*-

import codecs
import pywikibot
import urllib
import urllib2
import httplib
import re
import collections
import locale
import sjpMaintain
from morfeusz import *
from klasa import *
from lxml import etree, html
from sjpClass import kategoriaSlowa, checkHistory


def checkFlexSJP(forma):
	enie = [[u'enia', u'enie', u'eniu'], [u'eniem', u'eniom'], [u'eniach', u'eniami']]
	anie = [[u'ania', u'anie', u'aniu'], [u'aniem', u'aniom'], [u'aniach', u'aniami']]
	cie = [[u'cia', u'cie', u'ciu'], [u'ciem', u'ciom'], [u'ciach', u'ciami']]
	#parser = etree.HTMLParser()
	while True:
		try:
			web = html.parse('http://www.sjp.pl/%s' % urllib.quote(forma.encode('utf-8')))
		except IOError:
			return None
		break
	
	try: podstawowa = web.xpath('//b[@style="font-size: large;"]/a/text()')
	except AssertionError:
		return None
	try: flagi = web.xpath('//tt[1]/text()')
	except AssertionError:
		return None
	analyzed = analyse(forma, dag=1)
	search = None

	for elem in analyzed:
		if elem[2][2] and u'ger:' in elem[2][2]:
			search = 1
	
	if search and any('j' in s for s in flagi) or any('UV' in s for s in flagi) or any('i' in s for s in flagi):
		if forma[-3:] in cie[0]:
			return forma[:-3] + u'cie'
		elif forma[-4:] in anie[0]:
			return forma[:-4] + u'anie'
		elif forma[-4:] in enie[0]:
			return forma[:-4] + u'enie'
		elif forma[-4:] in cie[1]:
			return forma[:-4] + u'cie'
		elif forma[-5:] in anie[1]:
			return forma[:-5] + u'anie'
		elif forma[-5:] in enie[1]:
			return forma[:-5] + u'enie'
		elif forma[-5:] in cie[2]:
			return forma[:-5] + u'cie'
		elif forma[-6:] in anie[2]:
			return forma[:-6] + u'anie'
		elif forma[-6:] in enie[2]:
			return forma[:-6] + u'enie'
	elif len(podstawowa) == 1:
		return podstawowa[0]
	else:
		return None

	
class HasloSJP():
	def __init__(self, a, grabExisting = False):
		self.words = []
		self.numWords = 0
		self.type = 1
		self.problems = {u'kilka_znaczen' : 0, u'kilka_form_odmiany' : 0, u'synonimy' : 0, u'obcy' : 0, u'ndm' : 0, u'rodzaj' : 0, u'brak_znaczenia' : 0, u'przymiotnik_od' : 0}
		
		if not grabExisting:	
			try: ifExists = Haslo(a)
			except sectionsNotFound:
				pass
			else:
				if ifExists.type == 3:
					for b in ifExists.listLangs:
						if u'język polski' in b.langLong or u'termin obcy' in b.langLong or u'użycie międzynarodowe' in b.langLong:
							self.type = 0
					
		if self.type:
			if self.retrieve(a) == 0:
				self.type = 0
			else:
				self.meanings()
		


	def retrieve(self, a):
		parser = etree.HTMLParser()

		while True:
			try: sjpsite = urllib2.urlopen('http://www.sjp.pl/%s' % urllib.quote(a.encode('utf-8')))
			except urllib2.HTTPError:
				print u'httperror'
				return 0
			except urllib2.URLError:
				continue
			except httplib.BadStatusLine:
				continue
			break
	
		try:
			web = etree.parse(sjpsite, parser)
		except IOError:
			return 0	
	
                naglowek = web.xpath("//p/b/a[@class='lc']/text()")
		xp_dictionary = web.xpath("//table[@class='wtab']//tr[2]/td")
		xp_flex = web.xpath("//table[@class='wtab']//tr[3]/td")

		tables = []
		tbs = web.xpath("//table[@class='wtab']")
		for elem in tbs:
			tables.append(elem.xpath(".//tr//text()"))
			
		self.numWords = len(naglowek)
        	
		if tables == []:
			print u'jestem'
			print u'nie znaleziono strony na sjp.pl'
			return 0
		
                
		for j in range(self.numWords):
			xp_title = naglowek[j]
			
			if xp_title == a:
				temp = Word(unicode(xp_title))
				temp_mean = web.xpath("//p[@style='margin-top: .5em; font-size: medium; max-width: 32em; '][%d]/text()" % (j+1))
				mean = u'<br />'.join(temp_mean)
				temp.addTempMean(mean)
				#temp.addInGames(xp_inGames[j].text)
				temp.addDictionary(xp_dictionary[j].text)
				temp.addFlex(xp_flex[j].text)
				
				numTr = len(tables[j])/2
				
				for i in range(numTr-4):
					ii = i+3
				
					try:
						tables[j][2*ii]
					except IndexError:
						pass
					else:
						temp.addFlags([tables[j][2*ii-1], tables[j][2*ii].split(', ')])
							
				self.words.append(temp)
					
	def meanings(self):
		re_mean = re.compile('(?<![2-9])[0-9]\.(.*?)(?=<br />[0-9]\.|$)', re.DOTALL)
		re_osoba = re.compile('[0-9]{4}')
		#poniďż˝ej lista znaczeďż˝ odrzucanych od razu - moďż˝na siďż˝ zastanowiďż˝ nad imionami
		for a in self.words:
			s_osoba = re.search(re_osoba, a.tempMean)
			if a.tempMean == u'' or a.tempMean == u'(brak znaczenia)':
				a.tempMean = u''
				self.problems['brak_znaczenia'] = 1
			if s_osoba or u'nazwisko' in a.tempMean or u'wieś w' in a.tempMean or u'imię męskie' in a.tempMean or u'imię żeńskie' in a.tempMean:
				a.addMean(None)
				a.noMean = 1
			else:
				re_czytaj = re.compile(ur'\[czytaj\:(.*?)\]\s*')
				s_czytaj = re.search(re_czytaj, a.tempMean)
				if s_czytaj:
					a.obcy = 1
					a.wymowa = s_czytaj.group(1).strip()
					a.tempMean = re.sub(re_czytaj, u'', a.tempMean)
				s_mean = re.findall(re_mean, a.tempMean)
				if s_mean:
					for b in range(len(s_mean)):
						s_mean[b] = s_mean[b].strip()
						s_mean[b] = s_mean[b].rstrip(';')
						tempMean = Meaning(s_mean[b])
						a.addMean(tempMean)
				else:
					tempMean = Meaning(a.tempMean)
					a.addMean(tempMean)
		
	def checkProblems(self):
		self.problems[u'np'] = 0
		self.problems[u'zwrotny'] = 0
		for a in self.words:
			if len(a.meanings) > 1:
				self.problems[u'kilka_znaczen'] = 1
			elif len(a.meanings) == 1 and a.meanings[0] and u'{{przym}} od [[' in a.meanings[0].definition:
				self.problems[u'przymiotnik_od'] = 1
			for b in a.meanings:
				if b and u'np.' in b.definition:
					self.problems[u'np'] = 1
				if b and 'czasownik' in a.typeText and (u'[[%s]] [[się]]' % (a.title) in b.definition or u'[[%s się]]' % (a.title) in b.definition):
					self.problems[u'zwrotny'] = 1
					print u'problems zwrotny'
				if b and b.synonyms:
					self.problems[u'synonimy'] = 1
			if a.obcy:
				self.problems[u'obcy'] = 1
			if a.czescMowy == 2:
				self.problems[u'ndm'] = 1	

		
class Word():
	def __init__(self, title):
		self.title = title
		self.flags = []
		self.meanings = []
		self.czescMowy = 0 # możliwości: 1 rzeczownik, 2 ndm (nie wiadomo), 3 przymiotnik, 4 czasownik
		self.wikitable = u''
		self.typeText = u'{{brak|część mowy}}'
		self.blpm = 0
		self.noMean = 0
		self.morfeusz = 0
		self.morfeuszType = u''
		self.morfeuszAmbig = 0
		self.added = 0 # zmienna kontrolująca pojawienie się flagi "ręcznie dodane"
		self.wymowa = u''
		self.obcy = 0
		
		
	def addTempMean(self, tempMean):
		self.tempMean = tempMean
	
	def addInGames(self, inGames):
		self.inGames = inGames
	
	def addDictionary(self, dictionary):
		self.dictionary = dictionary
	
	def addFlex(self, flex):
		self.flex = flex
	
	def addFlags(self, flags):
		self.flags.append(flags)
		
	def addMean(self, Meaning):
		self.meanings.append(Meaning)
		
	def flexTable(self, odmianaOlafa):
		tablesg = {"nom": [], "gen": [], "dat": [], "acc": [], "inst": [], "loc": [], "voc": []}
		tablepl = {"nom": [], "gen": [], "dat": [], "acc": [], "inst": [], "loc": [], "voc": []}
		flagsSubs = [u'M', u'N', u'T', u'U', u'V', 'O', 'Q', 'D', 'o', 'q', 's', 'P', 'R', 'S', 'C', 'Z', 'w', 't', 'z', 'm', 'n']
		flagsAdj = [u'XYbx', u'Xbx', u'XYbxy', u'XYbx~', u'XYb(-b) cx', u'Xbx~', u'XYbxy~']
		flagsVerb = [u'B', u'H']
		blp = 0
		blm = 1 # kontrola liczby mnogiej - domyślnie jej nie ma
		ambig = 0 # kontrola formy podstawowej - jeżeli może być więcej niż jedną częścią mowy, pomijamy generowanie odmiany
		type = None
		
		if self.flex == u'nie':
			self.wikitable = u'{{nieodm}}'
			self.typeText = u'{{brak|część mowy}}'
			self.czescMowy = 2
		else:
			tempFlag = u''
			for a in self.flags:
				tempFlag += a[0]
				
			for a in flagsSubs:
				if a in tempFlag:
					type = u'subst'
					print a					
					break
			
			for a in flagsAdj:
				if tempFlag == a:
					type = u'adj'
					break
					
			for a in flagsVerb:
				if a in tempFlag:
					type = u'verb'
					break
			
			primaryTest = analyse(self.title, dag=1)
			if primaryTest[0][2][1]:
				self.morfeusz = 1
				prev = primaryTest[0][2][2].split(':')[0]
				for a in primaryTest:
					spl = a[2][2].split(':')
					if spl[0] != prev:
						self.morfeuszAmbig = 1
					else:
						prev = spl[0]
						
				if not ambig:
					self.morfeuszType = prev
				else:
					print u'morfeusz ambig'

			else:
				self.morfeusz = 0
				print u'morfeusz nie zna'
				
			for a in self.flags:
				if u'~' in a[0]:
					self.added = 1
			
			if type == u'':
				brak = b.title + u'\n'
				file = open('braki.txt', 'a')
				file.write(brak.encode( "utf-8" ))
				file.close
			
			if type == 'subst' and not self.morfeuszAmbig and self.morfeusz: 
				self.czescMowy = 1
				if len(self.flags):
					self.flags.append([u'1', [self.title]]) # dodanie słowa podstawowego jako flagi "1", żeby Morfeusz uwzględniał też formę podst.
				
				lowerCase = self.title[0].lower() + self.title[1:] # morfeusz formę podstawową zawsze zaczyna od małej litery - ten trik pozwala na szukanie odmiany nazw własnych
				temp = ''
				prev = ''
				depr = ''
				countGen = {"m1" : 0, "m2" : 0, "m3" : 0, "f" : 0, "n1" : 0, "n2" : 0, "p1" : 0, "p2" : 0, "p3" : 0} # zliczanie rodzajów zwróconych przez Morfeusza
				
				genflag = u''
				genflag = genFromFlags(self)
				
				for a in self.flags:
					for b in a[1]:
						morfeuszTemp = analyse(b, dag=1)
						#print morfeuszTemp
						if morfeuszTemp[0][2][2]:
							for c in morfeuszTemp:
								morf = c[2][2].split(':')
								if (morf[0] == 'subst' or morf[0] == 'depr') and (c[2][1] == self.title or c[2][1] == lowerCase):
									if morf[0] == 'subst' and morf[1] == 'sg':
										if u'%s' % c[2][0] not in tablesg[u'%s' % morf[2]]:
											tablesg[u'%s' % morf[2]].append(c[2][0])
									elif morf[0] == 'subst' and morf[1] == 'pl':
										if u'%s' % c[2][0] not in tablepl[u'%s' % morf[2]]:
											tablepl[u'%s' % morf[2]].append(c[2][0])
									if morf[0] == 'depr':
										depr = c[2][0]
									countGen['%s' % morf[3]] += 1
                                # ponieważ mianownik, biernik i wołacz zazwyczaj znajdują się wśród odmiany lp, trzeba sprawdzić resztę przypadków i na tej podstawie określić blm
				if len(tablepl['gen']) == 0 and len(tablepl['dat']) == 0 and len(tablepl['inst']) == 0 and len(tablepl['loc']) == 0: 
					blm = 1
				
				elif len(tablepl['nom']):
					if tablepl['nom'][0] not in tablepl['voc']:
						tablepl['voc'].append(tablepl['nom'][0])
					blm = 0
				
				if len(tablesg['nom']) == 0 and len(tablesg['gen']) == 0 and len(tablesg['dat']) == 0 and len(tablesg['acc']) == 0 and len(tablesg['inst']) == 0 and len(tablesg['loc']) == 0 and len(tablesg['voc']) == 0: 
					blp = 1

				if depr != '':
					if depr not in tablepl['nom']:
						tablepl['nom'].append(u'{{depr}} ' + depr)
					if depr not in tablepl['voc']:
						tablepl['voc'].append(u'{{depr}} ' + depr)
				#(w fazie rozwojowej) poniżej sprawdzanie, czy w tabelce może znajdować się wątpliwa odmiana

				'''if len(tablepl['nom']) > 1:
					if len(tablepl['nom']) == 2 and u'{{depr}}' in tablepl['nom']:
						pass
					else:
						self.problems['kilka_form_odmiany'] = 1
						
				for d in tablesg:
					if len(tablesg[d]) > 1:
						self.problems['kilka_form_odmiany'] = 1
						
				for d in tablepl:
					if d != u'nom' and d != u'voc':
						if len(tablepl[d]) > 1:
							self.problems['kilka_form_odmiany'] = 1
					'''
				cnt = 0 # licznik pokazujący czy znaleziono więcej niż 1 rodzaj
				found = u''
				sum = 0
				for a in countGen:
					sum += countGen[a]
				
				for a in countGen:
					if countGen[a] >= 0.7*sum:
						found = a
						cnt += 1
				
				if cnt != 1:
					self.typeText = u'\'\'rzeczownik, \'\'{{brak|rodzaj}}'
					#self.problems[u'rodzaj'] = 1
					
				else:
					if found == u'm1':
						self.typeText = u'\'\'rzeczownik, rodzaj męskoosobowy\'\''
					elif found == u'm2':
						self.typeText = u'\'\'rzeczownik, rodzaj męskozwierzęcy\'\''
					elif found == u'm3':
						self.typeText = u'\'\'rzeczownik, rodzaj męskorzeczowy\'\''
					elif found == u'f':
						self.typeText = u'\'\'rzeczownik, rodzaj żeński\'\''
					elif found == u'n2':
						self.typeText = u'\'\'rzeczownik, rodzaj nijaki\'\''
							
				
				self.wikitable += u'{{odmiana-rzeczownik-polski\n'
				if not blp:
					self.wikitable += u'|Mianownik lp = %s\n|Dopełniacz lp = %s\n|Celownik lp = %s\n|Biernik lp = %s\n|Narzędnik lp = %s\n|Miejscownik lp = %s\n|Wołacz lp = %s\n' % ("/".join(tablesg['nom']), "/".join(tablesg['gen']), "/".join(tablesg['dat']), "/".join(tablesg['acc']), "/".join(tablesg['inst']), "/".join(tablesg['loc']), "/".join(tablesg['voc']))
				else:
					self.blpm = 1
				if not blm:
					self.wikitable += u'|Mianownik lm = %s\n|Dopełniacz lm = %s\n|Celownik lm = %s\n|Biernik lm = %s\n|Narzędnik lm = %s\n|Miejscownik lm = %s\n|Wołacz lm = %s\n' % ("/".join(tablepl['nom']), "/".join(tablepl['gen']), "/".join(tablepl['dat']), "/".join(tablepl['acc']),  "/".join(tablepl['inst']), "/".join(tablepl['loc']), "/".join(tablepl['voc']))
				else:
					self.blpm = 2
				self.wikitable += u'}}'
			
			elif type == u'subst' and not self.morfeusz:
				self.czescMowy = 1
				gen = genFromFlags(self)
				if gen == u'm':
					self.typeText = u'\'\'rzeczownik, rodzaj męski\'\''
				elif gen == u'f':
					self.typeText = u'\'\'rzeczownik, rodzaj żeński\'\''
				elif gen == u'n':
					self.typeText = u'\'\'rzeczownik, rodzaj nijaki\'\''
				else:
					self.typeText = u'\'\'rzeczownik\'\''
					
			elif type == u'adj':
				self.czescMowy = 3
				countAdj = 0
				self.typeText = u'\'\'przymiotnik\'\''
				if self.title[-1] == u'y' or self.title[-1] == u'i':
					self.wikitable = u'{{odmiana-przymiotnik-polski|%s|bardziej %s}}' % (self.title, self.title)
			elif type == u'verb':
				self.czescMowy = 4
				self.typeText = u'\'\'czasownik\'\''
				temp = wezOdmiane(self, odmianaOlafa)
				if temp:
					self.wikitable += temp[0]
					if temp[1]:
						self.typeText = u'\'\'' + temp[1] + u'\'\''
						if u'czasownik' in temp[1] and u'przechodni' in temp[1]:
							self.typeText += u' ({{'
							if u'niedokonany' not in temp[1]:
								self.typeText += u'n'
							self.typeText += u'dk}} {{brak|aspekt}})'
							
				
			elif type == u'adv':
				self.czescMowy = 5
				self.typeText = u'\'\'przysłówek\'\''
				
				
			else:
				print u'czesc mowy != rzeczownik or przymiotnik or czasownik'
		
	

class OdmianaOlafa():
	def __init__(self):
		site = pywikibot.getSite()
		wzorceOdmianyWiki=pywikibot.Page(site, u'Wikipedysta:Olafbot/odmiana/wzorce')
		text = wzorceOdmianyWiki.get()
		self.wzorce = collections.defaultdict()
		self.wzorce_id = collections.defaultdict()
		self.wzorce_czescimowy = collections.defaultdict()
		
		id = None
		sjp_pl = None
		numer = 0
		lista = []
		lista = text.split(u'\n')
		for a in lista:
			if len(a)<1:
				continue
			if a[0]!=u'|':
				continue
			
			if (len(a)>1 and a[1]==u'-'):
				numer = 0
				id=None
				sjp_pl=None
			else:
				numer+=1
			
			if (numer==1 and len(a)>1):
				id=a[1:].strip()
			if (numer==3 and len(a)>1):
				sjp_pl=a[1:].strip()
			if (numer==4 and len(a)>1):
				slow=a[1:]
				if len(slow)<1:
					continue
				if slow[0] == u'|' and len(slow)>1:
					slow=slow[1:]
				slow=slow.strip()
				slow = slow.replace(u'\\n', u'\n')

				self.wzorce[sjp_pl]=slow
				self.wzorce_id[sjp_pl]=id
			if (numer == 5 and len(a)>1):
				czescmowy = a[1:].strip()
				self.wzorce_czescimowy[sjp_pl] = czescmowy

def wezOdmiane(word, odmOlafa):
	slowo = word.title
	odmiana = kodujOdmiane(word)
	if (odmiana == None):
		print u'brak w sjp'
		return None
	
	wzorzec = None
	try:
		wzorzec = odmOlafa.wzorce[odmiana]
	except KeyError:
		print u'brak w tabeli'
	try:
		id = odmOlafa.wzorce_id[odmiana]
	except KeyError:
		print u'brak id w tabeli'
	try:
		czescmowy = odmOlafa.wzorce_czescimowy[odmiana]
	except KeyError:
		print u'brak czesci mowy w tabeli'
	if wzorzec == None:
		print u'brak wzorca w tabeli'
		return None
	elif len(wzorzec)==0:
		print u'nieuzupelniony wzorzec'
		return None
	
	odj=0
	k=0
	s=odmiana.index(u'~')
	if s>=0:
		k=odmiana.index(u',')
		k=k-s
		if k<0:
			k=len(odmiana)
		odj=k-s-1
		
	if (odj>len(slowo) or s>=0 and not slowo[len(slowo)-odj:]==odmiana[s+1:k]):
		print slowo
		print odmiana[s+1:k]
		if odj<=len(slowo):
			print slowo[len(slowo)-odj:]
		print u'inna koncowka!'
		return None
	temat = slowo[:len(slowo)-odj]
	slowo2=u'			   ' + slowo
	temat1=slowo2[:len(slowo2)-odj-1].strip()
	temat2=slowo2[:len(slowo2)-odj-2].strip()
	wzorzec = wzorzec.replace(u'Q2', temat2)
	wzorzec = wzorzec.replace(u'Q1', temat1)
	wzorzec = wzorzec.replace(u'Q', temat)
	wynik = wzorzec
	return [wynik, czescmowy]

def kodujOdmiane(word,rdzen=0):
	slowo = word.title
	if (len(slowo)>1 and not slowo[0] == slowo[0].lower()):
		return None
	if (len(slowo)>2 and slowo[:-2] == u'zm'):
		return "zakonczone na -zm"
    
	odmianaTemp = []
	odmiana = []
	for a in word.flags:
		for b in a[1]:
			odmianaTemp.append(b)
	
        locale.setlocale(locale.LC_ALL, "pl_PL.UTF-8")
	odmianaTemp.sort(cmp=locale.strcoll)
	
	odmiana.append(slowo)
	for a in odmianaTemp:
		odmiana.append(a)

	
	if len(odmiana) == 1:
		return None
	n=0
	while(n<len(odmiana)):
		odm = odmiana[n]
		if (len(odm)>3 and odm[:3] == u'nie'):
			odmiana.remove(odm)
			n-=1
		n+=1
	if len(odmiana)<=1:
		return None
    
	wzor = odmiana[0]
	
	rdz=len(wzor)
	for n in range(len(wzor)):
		roznica = False
		for i in range(1, len(odmiana)):
			odm = odmiana[i]
			if (len(odm)<=n or odm[n] != wzor[n]):
				roznica = True
				break

		if roznica:
			rdz = n
			break
    	
	wynik = []
	if rdzen:
		wynik.append(wzor[:rdz])
	for i in range(len(odmiana)):
		if i>0:
			wynik.append(u', ')
		wynik.append(u'~')
		wynik.append(odmiana[i][rdz:])
	#print u''.join(wynik)
	return u''.join(wynik)
			
class Meaning():
	def __init__(self, temp_definition):
		re_definition = re.compile('(.*?)(;(?! [a-z]\))|$)')
		if u'a)' in temp_definition or u'b)' in temp_definition or u'c)' in temp_definition:
			self.synonyms = None
			s_definition = temp_definition
		else:
			self.synonyms = self.synonymsSearch(temp_definition)
			s_definition = re.search(re_definition, temp_definition)
			if s_definition:
				s_definition = s_definition.group(1)
			else:
				s_definition = temp_definition
		
		self.definition = meanProcess(s_definition)
		self.definition = wikilink(self.definition)
		
	
	def synonymsSearch(self, definition):
		re_synonyms = re.compile(';(?! [a-z]\))(.*)')
		s_synonyms = re.search(re_synonyms, definition)
		tab_synonyms_temp = []
		if s_synonyms:
			tab_synonyms = re.split(',|;', s_synonyms.group(1))
			for i in range(len(tab_synonyms)):
				tab_synonyms[i] = tab_synonyms[i].strip()
				if ' ' not in tab_synonyms[i]:
					tab_synonyms_temp.append(u'[[%s]]' % tab_synonyms[i])
		
			if tab_synonyms_temp:
				return tab_synonyms_temp
			else:
				return None
		else:
			return None		
		
def wikipage(hasloSJP, obrazki):
	
	ref_sjp = 0
	
	wstep = u''
	wymowa = u''
	znaczenia = u''
	odmiana = u''
	przyklady = u''
	skladnia = u''
	kolokacje = u''
	synonimy = u''
	antonimy = u''
	pokrewne = u''
	frazeologiczne = u''
	etymologia = u''
	uwagi = u''
	zrodla = u''
	
	wymowa_szablon = u'\n{{wymowa}}'
	znaczenia_szablon = u'\n{{znaczenia}}'
	odmiana_szablon = u'\n{{odmiana}}'
	przyklady_szablon = u'\n{{przykłady}}\n: (1.1)'
	skladnia_szablon = u'\n{{składnia}}'
	kolokacje_szablon = u'\n{{kolokacje}}'
	synonimy_szablon = u'\n{{synonimy}}'
	antonimy_szablon = u'\n{{antonimy}}'
	pokrewne_szablon = u'\n{{pokrewne}}'
	frazeologiczne_szablon = u'\n{{frazeologia}}'
	etymologia_szablon = u'\n{{etymologia}}'
	uwagi_szablon = u'\n{{uwagi}}'
	tlumaczenia_szablon = u'\n{{tłumaczenia}}'
	zrodla_szablon = u'\n{{źródła}}'
	
	i = 1
	firstWord = hasloSJP.words[0]
	for word in hasloSJP.words:
		if word.title == firstWord.title:
			j = 1
			if word.meanings[0]:
				znaczenia += u'\n%s' % (word.typeText)
				if word.blpm == 1 or word.blpm == 2 or word.wikitable != u'':
					odmiana += u'\n: (%d) ' % (i)
				if word.blpm == 1:
					odmiana += u'{{blp}} '
				elif word.blpm == 2:
					odmiana += u'{{blm}} '
				odmiana += word.wikitable
			for a in word.meanings:
				if a:
					a.definition = a.definition.strip()
					znaczenia += u'\n: (%d.%d) %s' % (i, j, a.definition)
					if not hasloSJP.problems['brak_znaczenia'] and not (hasloSJP.problems['przymiotnik_od'] and len(word.meanings) == 1):
						znaczenia += u'<ref name=sjp.pl/>'
						ref_sjp = 1
					if a.synonyms:
						synonimy += u'\n: (%d.%d) ' % (i, j) + ", ".join(a.synonyms)
					j += 1
					
				elif not a and i != 1:
					continue
				else:
					return 0
			i += 1
		
	if word.obcy and u'ą' not in firstWord.title and u'ę' not in firstWord.title and u'ó' not in firstWord.title and u'ń' not in firstWord.title and u'ć' not in firstWord.title and u'ś' not in firstWord.title:
		naglowek = u'== %s ({{termin obcy w języku polskim}}) ==' % firstWord.title
		wymowa = u' {{ortograficzny|%s}}' % firstWord.wymowa
	elif word.obcy:
		naglowek = u'== %s ({{język polski}}) ==' % firstWord.title
		wymowa = u' {{ortograficzny|%s}}' % firstWord.wymowa
	else:
		naglowek = u'== %s ({{język polski}}) ==' % firstWord.title
		
	
	try: obrazki[firstWord.title]
	except KeyError:
		pass
	else:
		for a in obrazki[firstWord.title]:
			wstep += u'\n' + a
	znaczenia = znaczenia_szablon + znaczenia
	odmiana = odmiana_szablon + odmiana

	# synonimy.ux.pl moved to dobryslownik.pl - need to find an alternative or parse dobryslownik
        # synTemp = synonimyUx(firstWord.title)
	# synonimy = synonimy_szablon + synonimy + synTemp[0]
        synTemp = [None, None]
        synonimy = synonimy_szablon + synonimy
	if synonimy == synonimy_szablon and hasloSJP.problems['brak_znaczenia']:
		hasloSJP.problems['brak_znaczenia'] = 2
	przyklady = przyklady_szablon + u' [%s szukaj przykładów w korpusie]' % (generateConcordationsLink(firstWord.title))
	kolokacje = kolokacje_szablon + u' [%s sprawdź kolokacje w korpusie]' % (generateCollocationsLink(firstWord.title))
	derived = derivedWordsLink(firstWord.title)
	pokrewne = pokrewne_szablon
	if derived:
		pokrewne = pokrewne + u' [%s sprawdź pokrewne w sjp.pl]' % (derived)
	wymowa = wymowa_szablon + wymowa
	zrodla = zrodla_szablon
	if ref_sjp or synTemp[1]:
		zrodla += u'\n<references>'
		if ref_sjp:
			zrodla += u'\n<ref name=sjp.pl>{{sjp.pl|%s}}</ref>' % (firstWord.title)
		if synTemp[1]:
			zrodla += u'\n<ref name=synonimy>{{synonimy.ux.pl}}</ref>'
		zrodla += u'\n</references>'

		
	finalText = naglowek + wstep + wymowa + znaczenia + odmiana + przyklady + skladnia_szablon + kolokacje + synonimy + antonimy_szablon + pokrewne + frazeologiczne_szablon + etymologia_szablon + uwagi_szablon + tlumaczenia_szablon + zrodla
	
	#print finalText
	return finalText		


		

def morfAnalyse(word):
	if word == u'':
		return [None, u'', None]
	analiza = analyse(word, dag=1)
	numWords = analiza[-1][1]
	count = [] # tablica z zerami do wyłapywania różnic w formach podstawowych
	count_first = [] # tablica z zerami do ustawiania pierwszego elementu dla danego słowa
	found = 0
	base = None
	form = u''
	text = ''
	for counter in range(numWords):
		count.append(0)
		count_first.append(0)
		seek_last = 0
		
		for a in analiza: #Morfeusz rozbija słowa z "ś" na końcu na coś + byś (wtedy w analizie pojawia się oznakowanie "aglt"
			if a[2][2] and u'aglt' in a[2][2]:
				count[counter] += 1
		for for_helper, element in enumerate(analiza):		
			#print element
			if element[0] == counter:
				if seek_last == 0:
					seek_last = 1
				if count_first[counter] == 0: # catch the first element
					pierwszy = element
					count_first[counter] = 1
				if element[2][1] != pierwszy[2][1]: # if base form is different from the base form of the first elem, ++counter
					count[counter] += 1
					break
			else:
				if seek_last == 1:
					seek_last = 2

			if seek_last == 2:
				for_helper -= 1
				break

		# to jest trochę ryzykowne: jeśli Morfeusz widzi niejednoznaczność, wtedy skrypt sprawdza czy w sjp.pl to słowo jest jednoznaczne. Przykład: "temu" w sjp.pl ma wskazuje tylko na formę podstawową "ten"
		if count[counter] or analiza[for_helper][2][1] == None:
			check = checkFlexSJP(word)
			if check:
				base = check
				form = word
				#text = text + shortLink(check, word)
			else:
				base = None
				form = analiza[for_helper][2][0]
				#text = text + analiza[for_helper][2][0]
			type = None
		elif analiza[for_helper][2][0] in ', ( ) ; - . : [ ]':
			base = None
			form = analiza[for_helper][2][0]
			#text = text + analiza[for_helper][2][0]
			type = None
		else:
			base = analiza[for_helper][2][1]
			form = analiza[for_helper][2][0]
			#text = text + shortLink(analiza[for_helper][2][1], analiza[for_helper][2][0])
			type = analiza[for_helper][2][2]
	
	return [base, form, type]
	
def shortLink(base, flex):
	if base == None:
		return flex
	else:
		if flex.startswith(base):
			suffix = flex.replace(base, u'')
			return u'[[%s]]%s' % (base, suffix)
		else:
			return u'[[%s|%s]]' % (base, flex)
			
def wikilink(phrase):
	phrase = phrase.strip()
	phraseTab = re.split(ur'\s*', phrase)

	dontAnalyse = [u'np.', u'm.in.', u'etc.', u'itd.', u'itp.', u'z', u'w', u'dzięki', u'co', u'po', u'pod', u'o']
	dontAnalyseNawias1 = []
	dontAnalyseNawias2 = []
	dontAnalyseNawiasy = []
	dontAnalysePrzecinek = []
	enieAnie = [u'eń', u'enia', u'enie', u'eniu', u'eniem', u'eniom', u'eniach', u'eniami', u'ań', u'ania', u'anie', u'aniu', u'aniem', u'aniom', u'aniach', u'aniami']
	dontAnalyse.append(u'od') # może być też od 'oda'
	dontAnalyse.append(u'być') # alt: "bycie"
	dontAnalyse.append(u'lub') # alt: "lubić"
	dontAnalyse.append(u'gdzieś') # rozbija na "gdzie" i "byś˝"
	dontAnalyse.append(u'albo') # alt: "alba"
	dontAnalyse.append(u'jak') # alt: "jaka" (okrycie wierzchnie)
	dontAnalyse.append(u'kawa') # alt: "Kawa" (?)
	dontAnalyse.append(u'sposób') # alt: "sposobić˝"
	dontAnalyse.append(u'iść') # alt: "iścić
	for a in dontAnalyse:
		dontAnalyseNawias1.append(u'(%s' % a)
		dontAnalyseNawias2.append(u'%s)' % a)
		dontAnalyseNawiasy.append(u'(%s)' % a)
		dontAnalysePrzecinek.append(u'%s,' % a)
	phraseOutput = u''
	
	re_przymiotnikOd = re.compile(ur'^przymiotnik od\:\s*(.*?)\s*$')
	s_przymiotnikOd = re.search(re_przymiotnikOd, phrase)
	if s_przymiotnikOd:
		phraseOutput += u'{{przym}} ''od'' [[%s]]' % s_przymiotnikOd.group(1)
	else:
		n = len(phraseTab)
		i = 0
		while (i<n):
			word = phraseTab[i]
			if word in dontAnalyse:
				phraseOutput += u' [[%s]]' % word
			elif word in dontAnalyseNawiasy:
				phraseOutput += u' ([[%s]])' % word[1:-1]
			elif word in dontAnalyseNawias1:
				phraseOutput += u' ([[%s]]' % word[1:]
			elif word in dontAnalyseNawias2:
				phraseOutput += u' [[%s]])' % word[:-1]
			elif word in dontAnalysePrzecinek:
				phraseOutput += u' [[%s]],' % word[:-1]
			elif word.endswith((u'enia', u'enie', u'eniu', u'eniem', u'eniom', u'eniach', u'eniami', u'ania', u'anie', u'aniu', u'aniem', u'aniom', u'aniach', u'aniami')):
				checked = checkFlexSJP(word)
				if checked:
					phraseOutput += u' %s' % shortLink(checked, word)
				else:
					phraseOutput += u' ' + shortLink(morfAnalyse(word)[0], morfAnalyse(word)[1])
			elif i<n-1 and (phraseTab[i+1] == u'się' or phraseTab[i+1] == u'się,' or phraseTab[i+1] == u'się.' or phraseTab[i+1] == u'się;' or phraseTab[i+1] == u'się)' or phraseTab[i+1] == u'się),' or phraseTab[i+1] == u'się);' or phraseTab[i+1] == u'się).') and morfAnalyse(word)[2] and (u'inf:' in morfAnalyse(word)[2] or u'pact:' in morfAnalyse(word)[2]):
				if phraseTab[i+1][-1] == u',' or phraseTab[i+1][-1] == u'.' or phraseTab[i+1][-1] == u':' or phraseTab[i+1][-1] == u')' or phraseTab[i+1][-1] == u';':
					phraseOutput += u' %s' % (shortLink(morfAnalyse(word)[0] + u' się', word + u' się')) + phraseTab[i+1][-1]
				elif phraseTab[i+1][-2:] == u'),' or phraseTab[i+1][-2:] == u').' or phraseTab[i+1][-2:] == u'):' or phraseTab[i+1][-2:] == u');':
					phraseOutput += u' %s' % (shortLink(morfAnalyse(word)[0] + u' się', word + u' się')) + phraseTab[i+1][-2:]
				else:
					phraseOutput += u' %s' % (shortLink(morfAnalyse(word)[0] + u' się', word + u' się'))
				i+=1
			else:
				if u'{{' in word and u'}}' in word:
					phraseOutput += u' %s' % word
				elif len(word) and ((word[0] == u'(' and word[-1] == u')') or (word[0] == u'(' and word[-1] == u',')):
					phraseOutput += u' (%s)' % shortLink(morfAnalyse(word[1:-1])[0], morfAnalyse(word[1:-1])[1])
				elif len(word) and word[0] == u'(':
					phraseOutput += u' (%s' % shortLink(morfAnalyse(word[1:])[0], morfAnalyse(word[1:])[1])
				elif len(word) and (word[-2:] == u'),' or word[-2:] == u').' or word[-2:] == u'):' or word[-2:] == u');'):
					phraseOutput += u' ' + shortLink(morfAnalyse(word[:-2])[0], morfAnalyse(word[:-2])[1]) + word[-2:] 
				elif len(word) and (word[-1] == u',' or word[-1] == u'.' or word[-1] == u':' or word[-1] == u')' or word[-1] == u';'):
					phraseOutput += u' ' + shortLink(morfAnalyse(word[:-1])[0], morfAnalyse(word[:-1])[1]) + word[-1]
				else:
					phraseOutput += u' ' + shortLink(morfAnalyse(word)[0], morfAnalyse(word)[1])
	
			i+=1
			phraseOutput = phraseOutput.strip()
		
	return phraseOutput
	
def meanProcess(mean):
	
	#obrďż˝bka znaczeďż˝
	mean = mean.replace(u'<br />', u' ')
	mean = mean.replace(u'dawniej:', u'{{daw}}')
	mean = mean.replace(u'zdrobnienie od:', u'{{zdrobn}}')
	mean = mean.replace(u'w językoznawstwie:', u'{{jęz}}')
	mean = mean.replace(u'w starożytności:', u'{{staroż}}')
	mean = mean.replace(u'w filozofii i w teologii:', u'{{filoz}} {{teol}}')
	mean = mean.replace(u'w literaturze:', u'{{liter}}')
	mean = mean.replace(u'potocznie:', u'{{pot}}')
	mean = mean.replace(u'pot.', u'{{pot}}')
	mean = mean.replace(u'w muzyce:', u'{{muz}}')
	mean = mean.replace(u'książkowo:', u'{{książk}}')
	mean = mean.replace(u'podniośle:', u'{{podn}}')
	mean = mean.replace(u'łowiectwo:', u'{{łow}}')
	mean = mean.replace(u'w prawie:', u'{{praw}}')
	mean = mean.replace(u'w sporcie:', u'{{sport}}')
	mean = mean.replace(u'przenośnie:', u'{{przen}}')
	mean = mean.replace(u'przen.', u'{{przen}}')
	mean = mean.replace(u'rzadko:', u'{{rzad}}')
	mean = mean.replace(u'przestarzale:', u'{{przest}}')
	
	return mean

def genFromFlags(word):
	temp = u''
	prev = u''
	for a in word.flags: # szukanie rodzaju na podstawie flagi (wg maila Kolaara), być może przydatne gdy Morfeusz nie oznaczy jednoznacznie
		if 'm' in a[0] or 'n' in a[0] or 'K' in a[0]:
			temp = 'f'
			if prev != '' and temp != prev:
				return u'k'
			else:
				prev = temp
		elif ('U' in a[0] and len(word.flags) == 1):
			temp = 'n'
			if prev != '' and temp != prev:
				return u'k'
			else:
				prev = temp
		elif 'O' in a[0] or 'Q' in a[0] or 'D' in a[0] or 'o' in a[0] or 'q' in a[0] or 'P' in a[0] or 'R' in a[0] or 'S' in a[0]or 'C' in a[0]  or 'Z' in a[0] or 'w' in a[0] or 't' in a[0] or 'z' in a[0]:
			temp = 'm'
			if prev != '' and temp != prev:
				return u'k'
			else:
				prev = temp
	if temp != u'':
		return temp
	else:
		return u'?'

def generateCollocationsLink(title):
	url = u'http://www.nkjp.uni.lodz.pl/collocations_meta.jsp?query=%s**&offset=0&limit=10000&span=0&collocationalContextLeft=1&collocationalContextRight=1&minCoocFreq=5&posOfCollocate=any&sort=srodek&preserve_order=true&dummystring=ąĄćĆęĘłŁńŃóÓśŚźŹżŻ&m_nkjpSubcorpus=balanced' % (title)
	return url

def generateConcordationsLink(title):
	url = u'http://www.nkjp.uni.lodz.pl/index_meta.jsp?query=%s**&offset=0&limit=100&span=0&sort=srodek&second_sort=srodek&groupBy=---&groupByLimit=1&preserve_order=true&dummystring=ąĄćĆęĘłŁńŃóÓśŚźŹżŻ&m_nkjpSubcorpus=balanced' % (title)
	return url

def ifalreadyexists(title, existing):

	if title in existing:
		return 0

	hasloWikt = Haslo(title)
	if hasloWikt.type == 3:
		for a in hasloWikt.listLangs:
			if u'język polski' in a.langLong or u'termin obcy' in a.langLong or u'użycie międzynarodowe' in a.langLong:
				return 0
	
	return 1


def kwalifAndLink(string):
	#funkcja do obsługi synonimy.ux.pl - dostaje jeden string stamtąd, zamienia kwalifikatory na nasze i dodaje wikilink
	kwal = [[u'[przestarz.]', u'{{przest}}'], [u'[żart.]', u'{{żart}}'], [u'[pot.]', u'{{pot}}'], [u'[książk.]', u'{{książk}}'], [u'[wulg.]', u'{{wulg}}'], [u'[specjalist.]', u'\'\'specjalistycznie\'\''], [u'[nadużyw.]', u'\'\'nadużywane\'\''], [u'[poet.]', u'{{poet}}'], [u'[oficj.]', u'{{ofic}}'], [u'[euf.]', u'{{eufem}}'], [u'[obraź.]', u'{{obraź}}']]
	found = 0
	for elem in kwal:
		if u' %s' % (elem[0]) in string:
			string = string.replace(u' %s' % (elem[0]), u'')
			string = elem[1] + u' [[' + string + u']]'
			found = 1
	if not found:
		string = u'[[' + string + u']]'
	return string

def synonimyUx(slowo):
	
	result = u''
	ref_syn = 0
	while True:
		try:
			web = html.parse('http://synonimy.ux.pl/multimatch.php?word=%s&search=1' % urllib.quote(slowo.encode('iso-8859-2')))
		except IOError:
			return result
		break
	
	podstawowa = web.xpath("//ul[@class='compact'][1]/li/a/@href")
	for elem in enumerate(podstawowa):
		while True:
			try:
				web1 = html.parse('http://synonimy.ux.pl/%s' % elem[1])
			except IOError:
				return u''
			break
		
		synonimy = web1.xpath("//table[@border='0']/tr/td/strong")
		resultPartial = u''
		if len(synonimy)>1:
			resultPartial = u'\n: {{brak|numer}}'
		for a in synonimy:
			if a.text != slowo:
				if resultPartial != u'\n: {{brak|numer}}':
					resultPartial += u', ' + kwalifAndLink(a.text)
				else:
					resultPartial += u' ' + kwalifAndLink(a.text)
		if len(synonimy)>3:
			resultPartial += u'<ref name=synonimy/>'
			ref_syn = 1
		
		result += resultPartial
	return [result, ref_syn]
					

def inProgress(kategorie):
	# returns a list of words that are on pages under verification
	strony = []
	for kat in kategorie:
		strony.append(kat.pages)
	re_words = re.compile(ur'== (.*?) \({{język polski}}\) ==')
	listInProgress = set()
	
	for page in strony:
		for i in range(60):
			wpage = pywikibot.Page(site, u'%s%d' % (page, i))
			if not checkHistory(wpage.title()):
				all = re.findall(re_words, wpage.get())
				for a in all:
					listInProgress.add(a)
					
	return listInProgress

def dontProcess():
	forbiddenSet = set()
	forbiddenPage = pywikibot.Page(site, u'Wikipedysta:AlkamidBot/sjp/wykluczone')
	for line in forbiddenPage.get().split(u'\n'):
		if line.strip() != '':
			forbiddenSet.add(line.strip())
	return forbiddenSet

def derivedWordsLink(title):
	#checks sjp.pl for the words with the same stem; returns a link if words are found, 0 if not
	parser = etree.HTMLParser()	
	
	#set the number of iterations: for >5 letter words, up to 4 stems will be checked, i.e. [zabierać, zabiera, zabier, zabie]
	#the iteration ends when the script finds at least two words with the stem; words marked as "not allowed in games" are not counted - most of them are proper nouns
	if len(title)>5:
		rng = 4
	elif len(title)>3:
		rng = len(title)-2
	else:
		rng = 1
	
	for i in range(rng):
		stem = title[:(len(title)-i)]
		while True:
			try: sjpsite = urllib2.urlopen('http://www.sjp.pl/slownik/lp.phtml?f_st=%s&f_en=&f_fl=-&f_msfl=-&f_mn=0&f_vl=0' % urllib.quote(stem.encode('utf-8')))
			except urllib2.HTTPError:
				print u'httperror'
				return 0
			except urllib2.URLError:
				continue
			except httplib.BadStatusLine:
				continue
			break
	
		try:
			web = etree.parse(sjpsite, parser)
		except IOError:
			return 0
		
		xp_deriv = web.xpath("//table[@class='ktb']//tr[not(@class='kbl')]//td[2]//text()")
		cnt = xp_deriv.count('tak') #counting the words allowed in word games
		if cnt>1:
			return u'http://www.sjp.pl/slownik/lp.phtml?f_st=%s&f_en=&f_fl=-&f_msfl=-&f_mn=0&f_vl=0' % stem
	return 0
		
def main():
		
	global site
	site = pywikibot.getSite()
	
	existing = [] # newly added words are stored in this list while the script is running, in case there are doubled words in the input list
	
	images =  obrazkiAndrzeja()
	odmOlafa = OdmianaOlafa()
	tabPage = pywikibot.Page(site, u'Wikipedysta:AlkamidBot/sjp/tabelka')
		
	wordsPerPage = 7 # how many pages we want on the output page for verification
	offline_mode = 0
	custom_list = 0

	#tutaj podaje sie liste slow do wprowadzenia (na poczatku kazdej linii powinno byc nowe slowo)
	inp = codecs.open('/home/adam/wikt/moje/importsjp/frequencyListPL.txt', encoding='utf-8')
	
	if custom_list == 1:
		inp = codecs.open(u'/home/adam/wikt/moje/importsjp/różne.txt', encoding=u'utf-8')
	
	lista = []
	i=1
	for line in inp:
		if i>500:
			break
		if line.strip() != u'':
			lista.append(line.split('=')[0].strip())
		i+=1
	

	kategorie = []
	kategorie.append(kategoriaSlowa(u'custom', wordsPerPage, u'różne/', u'\n|-\n| różne', u'custom'))
	kategorie.append(kategoriaSlowa(u'zwrotne', wordsPerPage, u'zwrotne/', u'\n|-\n| czasowniki zwrotne', u'zwrotne'))
	kategorie.append(kategoriaSlowa(u'ndm', wordsPerPage, u'ndm/', u'\n|-\n| nieodmienne', u'ndm'))
	kategorie.append(kategoriaSlowa(u'np', wordsPerPage, u'np/', u'\n|-\n| \"np.\" w znaczeniu', u'np'))
	kategorie.append(kategoriaSlowa(u'bezproblemu', wordsPerPage, u'łatwe/', u'\n|-\n| łatwe (jedno znaczenie, bez synonimów)', u'bezproblemu'))
	kategorie.append(kategoriaSlowa(u'reszta', wordsPerPage, u'wszystkie/', u'\n|-\n| reszta', u'reszta'))
	kategorie.append(kategoriaSlowa(u'brak_znaczenia', wordsPerPage, u'brak_znaczen/', u'\n|-\n| bez znaczeń', u'brak_znaczenia'))
	kategorie.append(kategoriaSlowa(u'przymiotnik_od', wordsPerPage, u'przymiotnik_od/', u'\n|-\n| \"przymiotnik od\"', u'przymiotnik_od'))
	
	tabelkaStart = u'{| class="wikitable"'
	tabelkaEnd = u'\n|}'
	
	forbidden = dontProcess()
	inprogress = inProgress(kategorie) #KONIECZNIE WŁĄCZYĆ PRZED IMPORTEM
	#inprogress = set()
	forbidden.union(inprogress)
	
	for i in lista:
		print i
		a = HasloSJP(i)
		if a.type:
			for b in a.words:
				b.flexTable(odmOlafa)
			a.checkProblems()
			if len(a.words):
                                
				b = a.words[0]
	
				if b.czescMowy in (1,2,3,4,5):
					naStrone = wikipage(a, images)
					if naStrone and ifalreadyexists(b.title, existing) and b.title not in forbidden:
						print 'tutaj'
						text = u''
						suma = 0
						complete = None
						for c in a.problems:
							suma += a.problems[c]
						
						if custom_list:
							which = u'custom'
						elif a.problems[u'zwrotny']:
							which = u'zwrotne'
						elif a.problems[u'przymiotnik_od']:
							which = u'przymiotnik_od'
						elif a.problems[u'np']:
							which = u'np'
						elif b.czescMowy == 2:
							which = u'ndm'
						elif a.problems[u'brak_znaczenia'] == 1:
							which = u'brak_znaczenia'
						elif a.problems[u'brak_znaczenia'] == 2:
							which = u'niedodawane'
						elif not suma:
							which = u'bezproblemu'
						else:
							which = u'reszta'
							
						for kat in kategorie:
							if which == kat.name:
								filename = kat.outputFile + u'%d.txt' % (kat.counter/wordsPerPage)
								outputPage = pywikibot.Page(site, u'%s%d' % (kat.pages, kat.counter/wordsPerPage))
								if kat.counter%wordsPerPage == 0:
									text += u'zweryfikowane=nie\nweryfikator=\n\n'
								if kat.counter%wordsPerPage == wordsPerPage-1:
									complete = kat.name
								kat.counter += 1
								kat.buffer += text + naStrone + u'\n\n'
						
						if complete:
							file_words = open(filename, 'w')
							
							for kat in kategorie:
								if complete == kat.name:
									kat.tabelka += u'\n| [[%s%d|%d]]' % (kat.pages, kat.counter/wordsPerPage-1, kat.counter/wordsPerPage-1)
									if not checkHistory(outputPage.title()):
										kat.counter += wordsPerPage-1
									else:
										file_words.write(kat.buffer.encode('utf-8'))
										if not offline_mode:
											outputPage.put(kat.buffer, comment=u'hasła zaimportowane z sjp.pl')
                                                                                else:
                                                                                        print kat.buffer
										kat.buffer = u''
							file_words.close
							file_tab = open(u'output/tabelka.txt', 'w')
							tabOutput = tabelkaStart
							for kat in kategorie:
								if '[[' in kat.tabelka: #add row only if there are entries (we don't want empty rows here)
									tabOutput += kat.tabelka
							tabOutput += tabelkaEnd
							file_tab.write(tabOutput.encode( "utf-8" ))
							file_tab.close
										
	
						print naStrone
						existing.append(u'%s' % b.title)
	
					elif not naStrone and ifalreadyexists(b.title, existing):
						file_niedodane = open('output/niedodane.txt', 'a')
						dodaj = u'*[[%s]]\n' % b.title
						file_niedodane.write(dodaj.encode("utf-8"))
						file_niedodane.close
	
	if not custom_list:
		tabPage.put(tabOutput, u'aktualizacja')
	
	if custom_list and filename and kategorie[0].buffer != u'':
		file_words = open(filename, 'w')
		kategorie[0].tabelka += u'\n| [[%s%d|%d]]' % (kategorie[0].pages, kategorie[0].counter/wordsPerPage, kategorie[0].counter/wordsPerPage)
		file_words.write(kategorie[0].buffer.encode('utf-8'))
		if not offline_mode:
			outputPage.put(kategorie[0].buffer, comment=u'hasła zaimportowane z sjp.pl')
		file_words.close

	inp.close
	if not custom_list:
		sjpMaintain.main()

if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
        
#TODO: uwaga na liczebniki, które mogą mieć taką samą flagę jak przymiotniki
