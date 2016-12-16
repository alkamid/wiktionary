#!/usr/bin/python
# -*- coding: iso-8859-2 -*-

import codecs
import pywikibot
import urllib.request, urllib.parse, urllib.error
import http.client
import re
import collections
import locale
import sjpMaintain
import pdb
from morfeusz import *
from klasa import *
from lxml import etree, html
from sjpClass import kategoriaSlowa, checkHistory



def checkFlexSJP(forma):
    enie = [['enia', 'enie', 'eniu'], ['eniem', 'eniom'], ['eniach', 'eniami']]
    anie = [['ania', 'anie', 'aniu'], ['aniem', 'aniom'], ['aniach', 'aniami']]
    cie = [['cia', 'cie', 'ciu'], ['ciem', 'ciom'], ['ciach', 'ciami']]
    #parser = etree.HTMLParser()
    while True:
        try:
            web = html.parse('http://www.sjp.pl/%s' % urllib.parse.quote(forma))
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
        if elem[2][2] and 'ger:' in elem[2][2]:
            search = 1

    if search and any('j' in s for s in flagi) or any('UV' in s for s in flagi) or any('i' in s for s in flagi):
        if forma[-3:] in cie[0]:
            return forma[:-3].lower() + 'cie'
        elif forma[-4:] in anie[0]:
            return forma[:-4].lower() + 'anie'
        elif forma[-4:] in enie[0]:
            return forma[:-4].lower() + 'enie'
        elif forma[-4:] in cie[1]:
            return forma[:-4].lower() + 'cie'
        elif forma[-5:] in anie[1]:
            return forma[:-5].lower() + 'anie'
        elif forma[-5:] in enie[1]:
            return forma[:-5].lower() + 'enie'
        elif forma[-5:] in cie[2]:
            return forma[:-5].lower() + 'cie'
        elif forma[-6:] in anie[2]:
            return forma[:-6].lower() + 'anie'
        elif forma[-6:] in enie[2]:
            return forma[:-6].lower() + 'enie'
    elif len(podstawowa) == 1:
        return str(podstawowa[0])
    else:
        return None


class HasloSJP():
    def __init__(self, a, grabExisting = False, noWiki = False):
        self.words = []
        self.numWords = 0
        self.type = 1
        self.problems = {'osoba': 0, 'kilka_znaczen' : 0, 'kilka_form_odmiany' : 0, 'synonimy' : 0, 'obcy' : 0, 'ndm' : 0, 'rodzaj' : 0, 'brak_znaczenia' : 0, 'przymiotnik_od' : 0}

        if not noWiki and not grabExisting:
            try: ifExists = Haslo(a)
            except sectionsNotFound:
                pass
            else:
                if ifExists.type == 3:
                    for b in ifExists.listLangs:
                        if 'język polski' in b.langLong or 'termin obcy' in b.langLong or 'użycie międzynarodowe' in b.langLong:
                            self.type = 0

        if self.type:
            if self.retrieve(a) == 0:
                self.type = 0
            else:
                self.meanings(noWiki)



    def retrieve(self, a):
        parser = etree.HTMLParser()

        while True:
            try: sjpsite = urllib.request.urlopen('http://www.sjp.pl/%s' % urllib.parse.quote(a))
            except urllib.error.HTTPError:
                print('httperror')
                return 0
            except urllib.error.URLError:
                continue
            except http.client.BadStatusLine:
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
            print('jestem')
            print('nie znaleziono strony na sjp.pl')
            return 0


        for j in range(self.numWords):
            xp_title = naglowek[j]

            if xp_title == a:
                temp = Word(str(xp_title))
                temp_mean = web.xpath("//p[@style='margin: .5em 0; font-size: medium; max-width: 32em; '][%d]/text()" % (j+1))
                mean = '<br />'.join(temp_mean)
                temp.addTempMean(mean)
                #temp.addInGames(xp_inGames[j].text)
                temp.addDictionary(xp_dictionary[j].text)
                temp.addFlex(xp_flex[j].text)

                numTr = len(tables[j])//2

                for i in range(numTr-4):
                    ii = i+3

                    try:
                        tables[j][2*ii]
                    except IndexError:
                        pass
                    else:
                        temp.addFlags([tables[j][2*ii-1], tables[j][2*ii].split(', ')])

                self.words.append(temp)
            else:		
                temp = Word(xp_title, notRoot = True)		
                self.words.append(temp)

    def meanings(self, noWiki=False):
        re_mean = re.compile('(?<![2-9])[0-9]\.(.*?)(?=<br />[0-9]\.|$)', re.DOTALL)
        re_osoba = re.compile('[0-9]{4}')
        #poniďż˝ej lista znaczeďż˝ odrzucanych od razu - moďż˝na siďż˝ zastanowiďż˝ nad imionami
        for a in self.words:
            if not a.notRoot:
                s_osoba = re.search(re_osoba, a.tempMean)
                if a.tempMean == '' or a.tempMean == '(brak znaczenia)':
                    a.tempMean = ''
                    self.problems['brak_znaczenia'] = 1
                if s_osoba or 'nazwisko' in a.tempMean or 'wieś w' in a.tempMean or 'imię męskie' in a.tempMean or 'imię żeńskie' in a.tempMean:
                    self.problems['osoba'] = 1
                    tempMean = Meaning(a.tempMean, noWiki)
                    a.addMean(tempMean)
                elif not noWiki:
                    re_czytaj = re.compile(r'\[czytaj\:(.*?)\]\s*')
                    s_czytaj = re.search(re_czytaj, a.tempMean)
                    if s_czytaj:
                        a.obcy = 1
                        a.wymowa = s_czytaj.group(1).strip()
                        a.tempMean = re.sub(re_czytaj, '', a.tempMean)
                    s_mean = re.findall(re_mean, a.tempMean)
                    if s_mean:
                        for b in range(len(s_mean)):
                            s_mean[b] = s_mean[b].strip()
                            s_mean[b] = s_mean[b].rstrip(';')
                            tempMean = Meaning(s_mean[b], noWiki)
                            a.addMean(tempMean)
                    else:
                        tempMean = Meaning(a.tempMean, noWiki)
                        a.addMean(tempMean)
                else:		
                    tempMean = Meaning(a.tempMean, noWiki)		
                    a.addMean(tempMean)

    def checkProblems(self):
        self.problems['np'] = 0
        self.problems['zwrotny'] = 0
        for a in self.words:
            if len(a.meanings) > 1:
                self.problems['kilka_znaczen'] = 1
            elif len(a.meanings) == 1 and a.meanings[0] and '{{przym}} od [[' in a.meanings[0].definition:
                self.problems['przymiotnik_od'] = 1
            for b in a.meanings:
                if b and 'np.' in b.definition:
                    self.problems['np'] = 1
                if b and 'czasownik' in a.typeText and ('[[%s]] [[się]]' % (a.title) in b.definition or '[[%s się]]' % (a.title) in b.definition):
                    self.problems['zwrotny'] = 1
                    print('problems zwrotny')
                if b and b.synonyms:
                    self.problems['synonimy'] = 1
            if a.obcy:
                self.problems['obcy'] = 1
            if a.czescMowy == 2:
                self.problems['ndm'] = 1


class Word():
    def __init__(self, title, notRoot = False):
        self.title = title
        self.notRoot = notRoot	
        self.flags = []
        self.meanings = []
        self.czescMowy = 0 # możliwości: 1 rzeczownik, 2 ndm (nie wiadomo), 3 przymiotnik, 4 czasownik
        self.wikitable = ''
        self.typeText = '{{brak|część mowy}}'
        self.blpm = 0
        self.noMean = 0
        self.morfeusz = 0
        self.morfeuszType = ''
        self.morfeuszAmbig = 0
        self.added = 0 # zmienna kontrolująca pojawienie się flagi "ręcznie dodane"
        self.wymowa = ''
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
        flagsSubs = ['M', 'N', 'T', 'U', 'V', 'O', 'Q', 'D', 'o', 'q', 's', 'P', 'R', 'S', 'C', 'Z', 'w', 't', 'z', 'm', 'n']
        flagsAdj = ['XYbx', 'Xbx', 'XYbxy', 'XYbx~', 'XYb(-b) cx', 'Xbx~', 'XYbxy~']
        flagsVerb = ['B', 'H']
        blp = 0
        blm = 1 # kontrola liczby mnogiej - domyślnie jej nie ma
        ambig = 0 # kontrola formy podstawowej - jeżeli może być więcej niż jedną częścią mowy, pomijamy generowanie odmiany
        type = None

        if self.flex == 'nie':
            self.wikitable = '{{nieodm}}'
            self.typeText = '{{brak|część mowy}}'
            self.czescMowy = 2
        else:
            tempFlag = ''
            for a in self.flags:
                tempFlag += a[0]

            for a in flagsSubs:
                if a in tempFlag:
                    type = 'subst'
                    print(a)
                    break

            for a in flagsAdj:
                if tempFlag == a:
                    type = 'adj'
                    break

            for a in flagsVerb:
                if a in tempFlag:
                    type = 'verb'
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
                    print('morfeusz ambig')

            else:
                self.morfeusz = 0
                print('morfeusz nie zna')

            for a in self.flags:
                if '~' in a[0]:
                    self.added = 1

            if type == '':
                brak = b.title + '\n'
                file = open('braki.txt', 'a')
                file.write(brak)
                file.close

            if type == 'subst' and not self.morfeuszAmbig and self.morfeusz:
                self.czescMowy = 1
                if len(self.flags):
                    self.flags.append(['1', [self.title]]) # dodanie słowa podstawowego jako flagi "1", żeby Morfeusz uwzględniał też formę podst.

                lowerCase = self.title[0].lower() + self.title[1:] # morfeusz formę podstawową zawsze zaczyna od małej litery - ten trik pozwala na szukanie odmiany nazw własnych
                temp = ''
                prev = ''
                depr = ''
                countGen = {"m1" : 0, "m2" : 0, "m3" : 0, "f" : 0, "n1" : 0, "n2" : 0, "p1" : 0, "p2" : 0, "p3" : 0} # zliczanie rodzajów zwróconych przez Morfeusza

                genflag = ''
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
                                        if '%s' % c[2][0] not in tablesg['%s' % morf[2]]:
                                            tablesg['%s' % morf[2]].append(c[2][0])
                                    elif morf[0] == 'subst' and morf[1] == 'pl':
                                        if '%s' % c[2][0] not in tablepl['%s' % morf[2]]:
                                            tablepl['%s' % morf[2]].append(c[2][0])
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
                        tablepl['nom'].append('{{depr}} ' + depr)
                    if depr not in tablepl['voc']:
                        tablepl['voc'].append('{{depr}} ' + depr)

                cnt = 0 # licznik pokazujący czy znaleziono więcej niż 1 rodzaj
                found = ''
                sum = 0
                for a in countGen:
                    sum += countGen[a]

                for a in countGen:
                    if countGen[a] >= 0.7*sum:
                        found = a
                        cnt += 1

                if cnt != 1:
                    self.typeText = '\'\'rzeczownik, \'\'{{brak|rodzaj}}'
                    #self.problems[u'rodzaj'] = 1

                else:
                    if found == 'm1':
                        self.typeText = '\'\'rzeczownik, rodzaj męskoosobowy\'\''
                    elif found == 'm2':
                        self.typeText = '\'\'rzeczownik, rodzaj męskozwierzęcy\'\''
                    elif found == 'm3':
                        self.typeText = '\'\'rzeczownik, rodzaj męskorzeczowy\'\''
                    elif found == 'f':
                        self.typeText = '\'\'rzeczownik, rodzaj żeński\'\''
                    elif found == 'n2':
                        self.typeText = '\'\'rzeczownik, rodzaj nijaki\'\''


                self.wikitable += '{{odmiana-rzeczownik-polski\n'
                if not blp:
                    self.wikitable += '|Mianownik lp = %s\n|Dopełniacz lp = %s\n|Celownik lp = %s\n|Biernik lp = %s\n|Narzędnik lp = %s\n|Miejscownik lp = %s\n|Wołacz lp = %s\n' % ("/".join(tablesg['nom']), "/".join(tablesg['gen']), "/".join(tablesg['dat']), "/".join(tablesg['acc']), "/".join(tablesg['inst']), "/".join(tablesg['loc']), "/".join(tablesg['voc']))
                else:
                    self.blpm = 1
                if not blm:
                    self.wikitable += '|Mianownik lm = %s\n|Dopełniacz lm = %s\n|Celownik lm = %s\n|Biernik lm = %s\n|Narzędnik lm = %s\n|Miejscownik lm = %s\n|Wołacz lm = %s\n' % ("/".join(tablepl['nom']), "/".join(tablepl['gen']), "/".join(tablepl['dat']), "/".join(tablepl['acc']),  "/".join(tablepl['inst']), "/".join(tablepl['loc']), "/".join(tablepl['voc']))
                else:
                    self.blpm = 2
                self.wikitable += '}}'

            elif type == 'subst' and not self.morfeusz:
                self.czescMowy = 1
                gen = genFromFlags(self)
                if gen == 'm':
                    self.typeText = '\'\'rzeczownik, rodzaj męski\'\''
                elif gen == 'f':
                    self.typeText = '\'\'rzeczownik, rodzaj żeński\'\''
                elif gen == 'n':
                    self.typeText = '\'\'rzeczownik, rodzaj nijaki\'\''
                else:
                    self.typeText = '\'\'rzeczownik\'\''

            elif type == 'adj':
                self.czescMowy = 3
                countAdj = 0
                self.typeText = '\'\'przymiotnik\'\''
                if self.title[-1] == 'y' or self.title[-1] == 'i':
                    self.wikitable = '{{odmiana-przymiotnik-polski|%s|bardziej %s}}' % (self.title, self.title)
            elif type == 'verb':
                self.czescMowy = 4
                self.typeText = '\'\'czasownik\'\''
                temp = wezOdmiane(self, odmianaOlafa)
                if temp:
                    self.wikitable += temp[0]
                    if temp[1]:
                        self.typeText = '\'\'' + temp[1] + '\'\''
                        if 'czasownik' in temp[1] and 'przechodni' in temp[1]:
                            self.typeText += ' ({{'
                            if 'niedokonany' not in temp[1]:
                                self.typeText += 'n'
                            self.typeText += 'dk}} {{brak|aspekt}})'


            elif type == 'adv':
                self.czescMowy = 5
                self.typeText = '\'\'przysłówek\'\''


            else:
                print('czesc mowy != rzeczownik or przymiotnik or czasownik')



class OdmianaOlafa():
    def __init__(self):
        site = pywikibot.getSite()
        wzorceOdmianyWiki=pywikibot.Page(site, 'Wikipedysta:Olafbot/odmiana/wzorce')
        text = wzorceOdmianyWiki.get()
        self.wzorce = collections.defaultdict()
        self.wzorce_id = collections.defaultdict()
        self.wzorce_czescimowy = collections.defaultdict()

        id = None
        sjp_pl = None
        numer = 0
        lista = []
        lista = text.split('\n')
        for a in lista:
            if len(a)<1:
                continue
            if a[0]!='|':
                continue

            if (len(a)>1 and a[1]=='-'):
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
                if slow[0] == '|' and len(slow)>1:
                    slow=slow[1:]
                slow=slow.strip()
                slow = slow.replace('\\n', '\n')

                self.wzorce[sjp_pl]=slow
                self.wzorce_id[sjp_pl]=id
            if (numer == 5 and len(a)>1):
                czescmowy = a[1:].strip()
                self.wzorce_czescimowy[sjp_pl] = czescmowy

def wezOdmiane(word, odmOlafa):
    slowo = word.title
    odmiana = kodujOdmiane(word)
    if (odmiana == None):
        print('brak w sjp')
        return None

    wzorzec = None
    try:
        wzorzec = odmOlafa.wzorce[odmiana]
    except KeyError:
        print('brak w tabeli')
    try:
        id = odmOlafa.wzorce_id[odmiana]
    except KeyError:
        print('brak id w tabeli')
    try:
        czescmowy = odmOlafa.wzorce_czescimowy[odmiana]
    except KeyError:
        print('brak czesci mowy w tabeli')
    if wzorzec == None:
        print('brak wzorca w tabeli')
        return None
    elif len(wzorzec)==0:
        print('nieuzupelniony wzorzec')
        return None

    odj=0
    k=0
    s=odmiana.index('~')
    if s>=0:
        k=odmiana.index(',')
        k=k-s
        if k<0:
            k=len(odmiana)
        odj=k-s-1

    if (odj>len(slowo) or s>=0 and not slowo[len(slowo)-odj:]==odmiana[s+1:k]):
        print(slowo)
        print(odmiana[s+1:k])
        if odj<=len(slowo):
            print(slowo[len(slowo)-odj:])
        print('inna koncowka!')
        return None
    temat = slowo[:len(slowo)-odj]
    slowo2='                           ' + slowo
    temat1=slowo2[:len(slowo2)-odj-1].strip()
    temat2=slowo2[:len(slowo2)-odj-2].strip()
    wzorzec = wzorzec.replace('Q2', temat2)
    wzorzec = wzorzec.replace('Q1', temat1)
    wzorzec = wzorzec.replace('Q', temat)
    wynik = wzorzec
    return [wynik, czescmowy]

def kodujOdmiane(word,rdzen=0):
    slowo = word.title
    if (len(slowo)>1 and not slowo[0] == slowo[0].lower()):
        return None
    if (len(slowo)>2 and slowo[:-2] == 'zm'):
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
        if (len(odm)>3 and odm[:3] == 'nie'):
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
            wynik.append(', ')
        wynik.append('~')
        wynik.append(odmiana[i][rdz:])
    #print u''.join(wynik)
    return ''.join(wynik)

class Meaning():
    def __init__(self, temp_definition, noWiki=False):
        re_definition = re.compile('(.*?)(;(?! [a-z]\))|$)')
        if noWiki:
            self.definition = temp_definition
        else:
            if 'a)' in temp_definition or 'b)' in temp_definition or 'c)' in temp_definition:
                self.synonyms = None
                s_definition = temp_definition
            else:
                self.synonyms = self.synonymsSearch(temp_definition)
                s_definition = re.search(re_definition, temp_definition)
                if s_definition:
                    s_definition = s_definition.group(1)
                else:
                    s_definition = temp_definition

        if not noWiki:
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
                    tab_synonyms_temp.append('[[%s]]' % tab_synonyms[i])

            if tab_synonyms_temp:
                return tab_synonyms_temp
            else:
                return None
        else:
            return None

def wikipage(hasloSJP, obrazki):

    ref_sjp = 0

    wstep = ''
    wymowa = ''
    znaczenia = ''
    odmiana = ''
    przyklady = ''
    skladnia = ''
    kolokacje = ''
    synonimy = ''
    antonimy = ''
    pokrewne = ''
    frazeologiczne = ''
    etymologia = ''
    uwagi = ''
    zrodla = ''

    wymowa_szablon = '\n{{wymowa}}'
    znaczenia_szablon = '\n{{znaczenia}}'
    odmiana_szablon = '\n{{odmiana}}'
    przyklady_szablon = '\n{{przykłady}}\n: (1.1)'
    skladnia_szablon = '\n{{składnia}}'
    kolokacje_szablon = '\n{{kolokacje}}'
    synonimy_szablon = '\n{{synonimy}}'
    antonimy_szablon = '\n{{antonimy}}'
    pokrewne_szablon = '\n{{pokrewne}}'
    frazeologiczne_szablon = '\n{{frazeologia}}'
    etymologia_szablon = '\n{{etymologia}}'
    uwagi_szablon = '\n{{uwagi}}'
    tlumaczenia_szablon = '\n{{tłumaczenia}}'
    zrodla_szablon = '\n{{źródła}}'

    i = 1
    firstWord = hasloSJP.words[0]
    for word in hasloSJP.words:
        if word.title == firstWord.title:
            j = 1
            if word.meanings[0]:
                znaczenia += '\n%s' % (word.typeText)
                if word.blpm == 1 or word.blpm == 2 or word.wikitable != '':
                    odmiana += '\n: (%d) ' % (i)
                if word.blpm == 1:
                    odmiana += '{{blp}} '
                elif word.blpm == 2:
                    odmiana += '{{blm}} '
                odmiana += word.wikitable
            for a in word.meanings:
                if a:
                    a.definition = a.definition.strip()
                    znaczenia += '\n: (%d.%d) %s' % (i, j, a.definition)
                    if not hasloSJP.problems['brak_znaczenia'] and not (hasloSJP.problems['przymiotnik_od'] and len(word.meanings) == 1):
                        znaczenia += '<ref name=sjp.pl/>'
                        ref_sjp = 1
                    if a.synonyms:
                        synonimy += '\n: (%d.%d) ' % (i, j) + ", ".join(a.synonyms)
                    j += 1

                elif not a and i != 1:
                    continue
                else:
                    return 0
            i += 1

    if word.obcy and 'ą' not in firstWord.title and 'ę' not in firstWord.title and 'ó' not in firstWord.title and 'ń' not in firstWord.title and 'ć' not in firstWord.title and 'ś' not in firstWord.title:
        naglowek = '== %s ({{termin obcy w języku polskim}}) ==' % firstWord.title
        wymowa = ' {{ortograficzny|%s}}' % firstWord.wymowa
    elif word.obcy:
        naglowek = '== %s ({{język polski}}) ==' % firstWord.title
        wymowa = ' {{ortograficzny|%s}}' % firstWord.wymowa
    else:
        naglowek = '== %s ({{język polski}}) ==' % firstWord.title


    try: obrazki[firstWord.title]
    except KeyError:
        pass
    else:
        for a in obrazki[firstWord.title]:
            wstep += '\n' + a
    znaczenia = znaczenia_szablon + znaczenia
    odmiana = odmiana_szablon + odmiana

    # synonimy.ux.pl moved to dobryslownik.pl - need to find an alternative or parse dobryslownik
    # synTemp = synonimyUx(firstWord.title)
    # synonimy = synonimy_szablon + synonimy + synTemp[0]
    synTemp = [None, None]
    synonimy = synonimy_szablon + synonimy
    if synonimy == synonimy_szablon and hasloSJP.problems['brak_znaczenia']:
        hasloSJP.problems['brak_znaczenia'] = 2
    przyklady = przyklady_szablon + ' [%s szukaj przykładów w korpusie]' % (generateConcordationsLink(firstWord.title))
    kolokacje = kolokacje_szablon + ' [%s sprawdź kolokacje w korpusie]' % (generateCollocationsLink(firstWord.title))
    derived = derivedWordsLink(firstWord.title)
    pokrewne = pokrewne_szablon
    if derived:
        pokrewne = pokrewne + ' [%s sprawdź pokrewne w sjp.pl]' % (derived)
    wymowa = wymowa_szablon + wymowa
    zrodla = zrodla_szablon
    if ref_sjp or synTemp[1]:
        zrodla += '\n<references>'
        if ref_sjp:
            zrodla += '\n<ref name=sjp.pl>{{sjp.pl|%s}}</ref>' % (firstWord.title)
        if synTemp[1]:
            zrodla += '\n<ref name=synonimy>{{synonimy.ux.pl}}</ref>'
        zrodla += '\n</references>'


    finalText = naglowek + wstep + wymowa + znaczenia + odmiana + przyklady + skladnia_szablon + kolokacje + synonimy + antonimy_szablon + pokrewne + frazeologiczne_szablon + etymologia_szablon + uwagi_szablon + tlumaczenia_szablon + zrodla

    #print finalText
    return finalText

def common_tag_part(tag1, tag2):
    common = ''
    len_tag2 = len(tag2)
    for i in range(len(tag1)):
        if i < len_tag2 and tag1[i] == tag2[i]:
            common += tag1[i]
        else:
            break
    return common.strip(':')

def morfAnalyse(word):
    if word == '':
        return [None, '', None]

    try: analiza = analyse(word, dag=1)
    except KeyError:
        return [word, word, None]

    numWords = analiza[-1][1]
    count = [] # tablica z zerami do wyłapywania różnic w formach podstawowych
    count_first = [] # tablica z zerami do ustawiania pierwszego elementu dla danego słowa
    found = 0
    base = None
    form = ''
    text = ''
    for counter in range(numWords):
        count.append(0)
        count_first.append(0)
        seek_last = 0

        for a in analiza: #Morfeusz rozbija słowa z "ś" na końcu na coś + byś (wtedy w analizie pojawia się oznakowanie "aglt"
            if a[2][2] and 'aglt' in a[2][2]:
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

    #When I updated to libmorfeusz2 on 18/02/2016, I realised sometimes ':a' or ':s'
    #was added to the end of the base form. Until I figure out what it is, I'll have
    #to use regex

    re_before_colon = re.compile(r'([^:]*)')
    if word == '':
        return [None, '', None]
    try: analysed = analyse(word, dag=1)
    except KeyError:
        return [None, word, None]

    if len(analysed) == 1:
        if analysed[0][2][2] == 'ign':
            analysed_return = [None, word, None]
        else:
            analysed_return = [re.match(re_before_colon, analysed[0][2][1]).group(1), word, analysed[0][2][2]]
    elif 'ppron3' in analysed[0][2][2]:
        #morfeusz links all 3rd person pronouns to 'on', so we'll skip them
        return [None, word, 'ppron3']
    else:
        base_form = re.match(re_before_colon, analysed[0][2][1]).group(1)
        ambig = 0
        common_tag = analysed[0][2][2]
        for elem in analysed:
            common_tag = common_tag_part(common_tag, elem[2][2])
            if re.match(re_before_colon, elem[2][1]).group(1) != base_form:
                ambig += 1
        if ambig == 0:
            analysed_return = [base_form, word, common_tag]
        elif ambig == 1 and analysed[-1][2][2] and analysed[-1][2][2].startswith('aglt:'):
            analysed_return = [base_form, word, None]
        else:
            return [None, word, None]

    return analysed_return


def shortLink(base, flex=None):
    if flex == None:
        flex = base[1]
        base = base[0]
    if base == None:
        return flex
    else:
        if flex.startswith(base):
            suffix = flex.replace(base, '')
            return '[[%s]]%s' % (base, suffix)
        else:
            return '[[%s|%s]]' % (base, flex)

def phrases_wikilink(input_text):
    text = []
    #https://regex101.com/r/dU5rE9/2
    re_wikilink_decompose = re.compile(r'\[\[([^\]\|]*)(?:\||)(.*?)\]\](\w*)', re.UNICODE)

    with open('input/phrases_under_4words.txt') as f:
        phraselist = f.read().splitlines()

    split_text = input_text.split()
    lengths = [len(line.split()) for line in phraselist]
    max_length = max(lengths)

    i = 0
    while (i < len(split_text)):
        word = split_text[i]
        if not ('[[' in word and ']]' in word):
            text.append(word)
            i += 1
            continue
        else:
            loop = True
            j = i
            outside_loop_control = 0
            cache = []
            while (loop):
                if j == len(split_text):
                    pass
                else:
                    s_decompose = re.search(re_wikilink_decompose, split_text[j])
                    if not s_decompose:
                        decomposed = (split_text[j], split_text[j])
                    elif s_decompose.group(3) != '' and s_decompose.group(2) == '':
                        decomposed = (s_decompose.group(1), s_decompose.group(1) + s_decompose.group(3))
                    elif s_decompose.group(2) == '':
                        decomposed = (s_decompose.group(1), s_decompose.group(1))
                    else:
                        decomposed = (s_decompose.group(1), s_decompose.group(2))
                    if j == i:
                        possible_phrases = [decomposed]
                    else:
                        possible_phrases = new_possible_phrases

                    new_possible_phrases = []

                    found = 0
                    for phr in possible_phrases:
                        if any(phrase.startswith((phr[0] + ' ' if j != i else '') + decomposed[0]) for phrase in phraselist):
                            found = 1
                            new_possible_phrases.append(((phr[0] + ' ' if j != i else '') + decomposed[0], (phr[1] + ' ' if j!= i else '') + decomposed[1]))

                        if decomposed[1] != decomposed[0] and any(phrase.startswith((phr[0] + ' ' if j != i else '') + decomposed[1]) for phrase in phraselist):
                            new_possible_phrases.append(((phr[0] + ' ' if j != i else '') + decomposed[1], (phr[1] + ' ' if j!= i else '') + decomposed[1]))
                            found = 1

                        if decomposed[1][0].isupper() and any(phrase.startswith((phr[0] + ' ' if j != i else '') + decomposed[0].title()) for phrase in phraselist):
                            found = 1
                            new_possible_phrases.append(((phr[0] + ' ' if j != i else '') + decomposed[0].title(), (phr[1] + ' ' if j!= i else '') + decomposed[1]))

                    cache.append(split_text[j])

                    if found:
                        j += 1
                        continue

                if len(new_possible_phrases) == 0 and len(set(possible_phrases)) == 1 and possible_phrases[0][0] in phraselist:
                    text.append(shortLink(possible_phrases[0][0], possible_phrases[0][1]))
                    loop = False
                    i = j 
                elif len(set(new_possible_phrases)) == 1 and new_possible_phrases[0][0] in phraselist:
                    text.append(shortLink(new_possible_phrases[0][0], new_possible_phrases[0][1]))
                    loop = False
                    i = j + 1
                elif len(cache) == 1:
                    text += cache
                    loop = False
                    i = j + 1
                else:
                    text += cache[:-1]
                    loop = False
                    i = j
    return ' '.join(text)

class AnalysedWord(object):
    def __init__(self, word, baseform=None, tag=None):
        self.word = word
        self.baseform = baseform
        self.tag = tag
    
    def __str__(self):
        return self.word

def find_reflective_verbs(input_list):
    #this was an early attempt to solve issue #46, but then I realised
    #that we can (almost) never be sure that there is only one verb in the phrase
    #because situations where all words are tagged are very rare. So it
    #seems that finding reflective is a futile task.
    reflective_only = ['boczyć', 'wykluć']
    verb_tags = ('inf', 'fin', 'pact', 'ppas', 'pcon', 'pant', 'imps', 'impt', 'praet')

    sumverbs = sum([any(vtag in word.tag for vtag in verb_tags) for word in input_list if (type(word) == AnalysedWord and word.tag)])
    vrbs = []
    for w in input_list:
        if type(w) == AnalysedWord and w.tag:
            found = any(vtag in w.tag for vtag in verb_tags)
            vrbs.append(found)

    print(vrbs)
    for word in input_list:
        if type(word) == AnalysedWord and (word.baseform in reflective_only or (word.tag and any(vtag in word.tag for vtag in verb_tags))):
            word.baseform += ' się'
            tmp_bf = word.baseform
    if 'tmp_bf' in locals():
        for word in input_list:
            if str(word) == 'się':
                word.baseform = tmp_bf

    return input_list

def wikilink(phrase):
    phrase = phrase.strip()
    phraseTab = re.split(r'\s*', phrase)
    outputPhrase = []

    # https://regex101.com/r/yB6tQ8/7
    re_punctuation_around = re.compile(r'^([\W]*?)([\w-]+?)([\W]*?)$')
    re_nonwords_only = re.compile(r'\w')

    dontAnalyse = ['np.', 'm.in.', 'etc.', 'itd.', 'itp.', 'z', 'w', 'dzięki', 'co', 'po', 'pod', 'o', 'se']
    enieAnie = ('enia', 'enie', 'eniu', 'eniem', 'eniom', 'eniach', 'eniami', 'ań', 'ania', 'anie', 'aniu', 'aniem', 'aniom', 'aniach', 'aniami')
    dontAnalyse.append('od') # alt: "oda"
    dontAnalyse.append('być') # alt: "bycie"
    dontAnalyse.append('lub') # alt: "lubić"
    dontAnalyse.append('gdzieś') # rozbija na "gdzie" i "byś˝"
    dontAnalyse.append('albo') # alt: "alba"
    dontAnalyse.append('jak') # alt: "jaka" (okrycie wierzchnie)
    dontAnalyse.append('kawa') # alt: "Kawa" (?)
    dontAnalyse.append('sposób') # alt: "sposobić˝"
    dontAnalyse.append('iść') # alt: "iścić
    dontAnalyse.append('dzień') # alt: dzienia, dzienie, dzienić (?)

    #so far I only found baseform ambiguity in pronouns where there was none in reality
    hardcoded_baseforms = [('jej', 'ona'), ('niej', 'ona'), ('ją', 'ona'), ('nią', 'ona')]
    temp_capital = []
    for elem in hardcoded_baseforms:
        temp_capital.append((elem[0].title(), elem[1]))
    hardcoded_baseforms += temp_capital

    #add all the words from dontAnalyse (and their titlecase versions)
    for elem in dontAnalyse:
        hardcoded_baseforms.append((elem, elem))
        hardcoded_baseforms.append((elem.title(), elem))

    #http://www.ipipan.waw.pl/~wolinski/publ/znakowanie.pdf
    verb_tags = ('inf', 'fin', 'pact', 'ppas', 'pcon', 'pant', 'imps', 'impt', 'praet')

    phraseOutput = ''
    re_przymiotnikOd = re.compile(r'^przymiotnik od\:\s*(.*?)\s*$')
    s_przymiotnikOd = re.search(re_przymiotnikOd, phrase)
    if s_przymiotnikOd:
        phraseOutput += '{{przym}} ''od'' [[%s]]' % s_przymiotnikOd.group(1)
    else:
        for word in phraseTab:
            s_nonword_only = re.search(re_nonwords_only, word)
            s_punctuation_around = re.search(re_punctuation_around, word)

            if s_nonword_only == None:
                outputPhrase.append(' ')
                outputPhrase.append(AnalysedWord(word))
                phraseOutput += ' ' + word            
            elif s_punctuation_around:
                analysed = ''
                s_word = s_punctuation_around.group(2)
                if s_word in [a[0] for a in hardcoded_baseforms]:
                    for a in hardcoded_baseforms:
                        if s_word == a[0]:
                            analysed = AnalysedWord(a[0], a[1], 'hardcoded')
                elif s_word.endswith(enieAnie):
                    checked = checkFlexSJP(s_word)
                    if checked:
                        analysed = AnalysedWord(s_word, checked, 'sjp')
                    else:
                        tmp = morfAnalyse(s_word)
                        analysed = AnalysedWord(tmp[1], tmp[0], tmp[2])
                elif s_word == 'się':
                    analysed = AnalysedWord(s_word)
                elif len(s_word):
                    if '{{' in s_punctuation_around.group(1) and '}}' in s_punctuation_around.group(3):
                        analysed = AnalysedWord(s_word)
                    else:
                        tmp = morfAnalyse(s_word)
                        analysed = AnalysedWord(tmp[1], tmp[0], tmp[2])

                outputPhrase.append(' {0}'.format(s_punctuation_around.group(1)))
                outputPhrase.append(analysed)
                outputPhrase.append(s_punctuation_around.group(3))
            else:
                outputPhrase.append(' ')
                outputPhrase.append(word)

        string_output = ''
        for elem in outputPhrase:
            try: bf = elem.baseform
            except AttributeError:
                string_output += str(elem)
            else:
                if elem.baseform:
                    string_output += shortLink(elem.baseform, elem.word)
                else:
                    string_output += str(elem)

    return string_output.strip()


def meanProcess(mean):

    #obróbka znaczeń
    mean = mean.replace('<br />', ' ')
    mean = mean.replace('dawniej:', '{{daw}}')
    mean = mean.replace('zdrobnienie od:', '{{zdrobn}}')
    mean = mean.replace('w językoznawstwie:', '{{jęz}}')
    mean = mean.replace('w starożytności:', '{{staroż}}')
    mean = mean.replace('w filozofii i w teologii:', '{{filoz}} {{teol}}')
    mean = mean.replace('w literaturze:', '{{liter}}')
    mean = mean.replace('potocznie:', '{{pot}}')
    mean = mean.replace('pot.', '{{pot}}')
    mean = mean.replace('w muzyce:', '{{muz}}')
    mean = mean.replace('książkowo:', '{{książk}}')
    mean = mean.replace('podniośle:', '{{podn}}')
    mean = mean.replace('łowiectwo:', '{{łow}}')
    mean = mean.replace('w prawie:', '{{praw}}')
    mean = mean.replace('w sporcie:', '{{sport}}')
    mean = mean.replace('przenośnie:', '{{przen}}')
    mean = mean.replace('przen.', '{{przen}}')
    mean = mean.replace('rzadko:', '{{rzad}}')
    mean = mean.replace('przestarzale:', '{{przest}}')

    return mean

def genFromFlags(word):
    temp = ''
    prev = ''
    for a in word.flags: # szukanie rodzaju na podstawie flagi (wg maila Kolaara), być może przydatne gdy Morfeusz nie oznaczy jednoznacznie
        if 'm' in a[0] or 'n' in a[0] or 'K' in a[0]:
            temp = 'f'
            if prev != '' and temp != prev:
                return 'k'
            else:
                prev = temp
        elif ('U' in a[0] and len(word.flags) == 1):
            temp = 'n'
            if prev != '' and temp != prev:
                return 'k'
            else:
                prev = temp
        elif 'O' in a[0] or 'Q' in a[0] or 'D' in a[0] or 'o' in a[0] or 'q' in a[0] or 'P' in a[0] or 'R' in a[0] or 'S' in a[0]or 'C' in a[0]  or 'Z' in a[0] or 'w' in a[0] or 't' in a[0] or 'z' in a[0]:
            temp = 'm'
            if prev != '' and temp != prev:
                return 'k'
            else:
                prev = temp
    if temp != '':
        return temp
    else:
        return '?'

def generateCollocationsLink(title):
    url = 'http://www.nkjp.uni.lodz.pl/collocations_meta.jsp?query=%s**&offset=0&limit=10000&span=0&collocationalContextLeft=1&collocationalContextRight=1&minCoocFreq=5&posOfCollocate=any&sort=srodek&preserve_order=true&dummystring=ąĄćĆęĘłŁńŃóÓśŚźŹżŻ&m_nkjpSubcorpus=balanced' % (title)
    return url

def generateConcordationsLink(title):
    url = 'http://www.nkjp.uni.lodz.pl/index_meta.jsp?query=%s**&offset=0&limit=100&span=0&sort=srodek&second_sort=srodek&groupBy=---&groupByLimit=1&preserve_order=true&dummystring=ąĄćĆęĘłŁńŃóÓśŚźŹżŻ&m_nkjpSubcorpus=balanced' % (title)
    return url

def ifalreadyexists(title, existing):

    if title in existing:
        return 0

    hasloWikt = Haslo(title)
    if hasloWikt.type == 3:
        for a in hasloWikt.listLangs:
            if 'język polski' in a.langLong or 'termin obcy' in a.langLong or 'użycie międzynarodowe' in a.langLong:
                return 0

    return 1


def kwalifAndLink(string):
    #funkcja do obsługi synonimy.ux.pl - dostaje jeden string stamtąd, zamienia kwalifikatory na nasze i dodaje wikilink
    kwal = [['[przestarz.]', '{{przest}}'], ['[żart.]', '{{żart}}'], ['[pot.]', '{{pot}}'], ['[książk.]', '{{książk}}'], ['[wulg.]', '{{wulg}}'], ['[specjalist.]', '\'\'specjalistycznie\'\''], ['[nadużyw.]', '\'\'nadużywane\'\''], ['[poet.]', '{{poet}}'], ['[oficj.]', '{{ofic}}'], ['[euf.]', '{{eufem}}'], ['[obraź.]', '{{obraź}}']]
    found = 0
    for elem in kwal:
        if ' %s' % (elem[0]) in string:
            string = string.replace(' %s' % (elem[0]), '')
            string = elem[1] + ' [[' + string + ']]'
            found = 1
    if not found:
        string = '[[' + string + ']]'
    return string

def synonimyUx(slowo):

    result = ''
    ref_syn = 0
    while True:
        try:
            web = html.parse('http://synonimy.ux.pl/multimatch.php?word=%s&search=1' % urllib.parse.quote(slowo.encode('iso-8859-2')))
        except IOError:
            return result
        break

    podstawowa = web.xpath("//ul[@class='compact'][1]/li/a/@href")
    for elem in enumerate(podstawowa):
        while True:
            try:
                web1 = html.parse('http://synonimy.ux.pl/%s' % elem[1])
            except IOError:
                return ''
            break

        synonimy = web1.xpath("//table[@border='0']/tr/td/strong")
        resultPartial = ''
        if len(synonimy)>1:
            resultPartial = '\n: {{brak|numer}}'
        for a in synonimy:
            if a.text != slowo:
                if resultPartial != '\n: {{brak|numer}}':
                    resultPartial += ', ' + kwalifAndLink(a.text)
                else:
                    resultPartial += ' ' + kwalifAndLink(a.text)
        if len(synonimy)>3:
            resultPartial += '<ref name=synonimy/>'
            ref_syn = 1

        result += resultPartial
    return [result, ref_syn]


def inProgress(kategorie):
    # returns a list of words that are on pages under verification
    strony = []
    for kat in kategorie:
        strony.append(kat.pages)
    re_words = re.compile(r'== (.*?) \({{język polski}}\) ==')
    listInProgress = set()

    for page in strony:
        for i in range(60):
            wpage = pywikibot.Page(site, '%s%d' % (page, i))
            if not checkHistory(wpage.title()):
                all = re.findall(re_words, wpage.get())
                for a in all:
                    listInProgress.add(a)

    return listInProgress

def dontProcess():
    forbiddenSet = set()
    forbiddenPage = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/sjp/wykluczone')
    for line in forbiddenPage.get().split('\n'):
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
            try: sjpsite = urllib.request.urlopen('http://www.sjp.pl/slownik/lp.phtml?f_st=%s&f_en=&f_fl=-&f_msfl=-&f_mn=0&f_vl=0' % urllib.parse.quote(stem))
            except urllib.error.HTTPError:
                print('httperror')
                return 0
            except urllib.error.URLError:
                continue
            except http.client.BadStatusLine:
                continue
            break

        try:
            web = etree.parse(sjpsite, parser)
        except IOError:
            return 0

        xp_deriv = web.xpath("//table[@class='ktb']//tr[not(@class='kbl')]//td[2]//text()")
        cnt = xp_deriv.count('tak') #counting the words allowed in word games
        if cnt>1:
            return 'http://www.sjp.pl/slownik/lp.phtml?f_st=%s&f_en=&f_fl=-&f_msfl=-&f_mn=0&f_vl=0' % stem
    return 0

def main():

    global site
    site = pywikibot.getSite()

    existing = [] # newly added words are stored in this list while the script is running, in case there are doubled words in the input list

    images =  obrazkiAndrzeja()
    odmOlafa = OdmianaOlafa()
    tabPage = pywikibot.Page(site, 'Wikipedysta:AlkamidBot/sjp/tabelka')

    wordsPerPage = 7 # how many pages we want on the output page for verification
    offline_mode = 0
    custom_list = 0

    #tutaj podaje sie liste slow do wprowadzenia (na poczatku kazdej linii powinno byc nowe slowo)
    inp = codecs.open('/home/adam/wikt/moje/importsjp/frequencyListPL.txt', encoding='utf-8')

    if custom_list == 1:
        inp = codecs.open('/home/adam/wikt/moje/importsjp/różne.txt', encoding='utf-8')

    lista = []
    i=1
    for line in inp:
        if i>500:
            break
        if line.strip() != '':
            lista.append(line.split('=')[0].strip())
        i+=1


    kategorie = []
    kategorie.append(kategoriaSlowa('custom', wordsPerPage, 'różne/', '\n|-\n| różne', 'custom'))
    kategorie.append(kategoriaSlowa('zwrotne', wordsPerPage, 'zwrotne/', '\n|-\n| czasowniki zwrotne', 'zwrotne'))
    kategorie.append(kategoriaSlowa('ndm', wordsPerPage, 'ndm/', '\n|-\n| nieodmienne', 'ndm'))
    kategorie.append(kategoriaSlowa('np', wordsPerPage, 'np/', '\n|-\n| \"np.\" w znaczeniu', 'np'))
    kategorie.append(kategoriaSlowa('bezproblemu', wordsPerPage, 'łatwe/', '\n|-\n| łatwe (jedno znaczenie, bez synonimów)', 'bezproblemu'))
    kategorie.append(kategoriaSlowa('reszta', wordsPerPage, 'wszystkie/', '\n|-\n| reszta', 'reszta'))
    kategorie.append(kategoriaSlowa('brak_znaczenia', wordsPerPage, 'brak_znaczen/', '\n|-\n| bez znaczeń', 'brak_znaczenia'))
    kategorie.append(kategoriaSlowa('przymiotnik_od', wordsPerPage, 'przymiotnik_od/', '\n|-\n| \"przymiotnik od\"', 'przymiotnik_od'))

    tabelkaStart = '{| class="wikitable"'
    tabelkaEnd = '\n|}'

    forbidden = dontProcess()
    inprogress = inProgress(kategorie) #KONIECZNIE WŁĄCZYĆ PRZED IMPORTEM
    #inprogress = set()
    forbidden.union(inprogress)

    for i in lista:
        print(i)
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
                        print('tutaj')
                        text = ''
                        suma = 0
                        complete = None
                        for c in a.problems:
                            suma += a.problems[c]

                        if custom_list:
                            which = 'custom'
                        elif a.problems['zwrotny']:
                            which = 'zwrotne'
                        elif a.problems['przymiotnik_od']:
                            which = 'przymiotnik_od'
                        elif a.problems['np']:
                            which = 'np'
                        elif b.czescMowy == 2:
                            which = 'ndm'
                        elif a.problems['brak_znaczenia'] == 1:
                            which = 'brak_znaczenia'
                        elif a.problems['brak_znaczenia'] == 2:
                            which = 'niedodawane'
                        elif not suma:
                            which = 'bezproblemu'
                        else:
                            which = 'reszta'

                        for kat in kategorie:
                            if which == kat.name:
                                filename = kat.outputFile + '%d.txt' % (kat.counter/wordsPerPage)
                                outputPage = pywikibot.Page(site, '%s%d' % (kat.pages, kat.counter/wordsPerPage))
                                if kat.counter%wordsPerPage == 0:
                                    text += 'zweryfikowane=nie\nweryfikator=\n\n'
                                if kat.counter%wordsPerPage == wordsPerPage-1:
                                    complete = kat.name
                                kat.counter += 1
                                kat.buffer += text + naStrone + '\n\n'

                        if complete:
                            file_words = open(filename, 'w')

                            for kat in kategorie:
                                if complete == kat.name:
                                    kat.tabelka += '\n| [[%s%d|%d]]' % (kat.pages, kat.counter/wordsPerPage-1, kat.counter/wordsPerPage-1)
                                    if not checkHistory(outputPage.title()):
                                        kat.counter += wordsPerPage-1
                                    else:
                                        file_words.write(kat.buffer)
                                        if not offline_mode:
                                            outputPage.put(kat.buffer, comment='hasła zaimportowane z sjp.pl')
                                        else:
                                            print(kat.buffer)
                                        kat.buffer = ''
                            file_words.close
                            file_tab = open('output/tabelka.txt', 'w')
                            tabOutput = tabelkaStart
                            for kat in kategorie:
                                if '[[' in kat.tabelka: #add row only if there are entries (we don't want empty rows here)
                                    tabOutput += kat.tabelka
                            tabOutput += tabelkaEnd
                            file_tab.write(tabOutput)
                            file_tab.close


                        print(naStrone)
                        existing.append('%s' % b.title)

                    elif not naStrone and ifalreadyexists(b.title, existing):
                        file_niedodane = open('output/niedodane.txt', 'a')
                        dodaj = '*[[%s]]\n' % b.title
                        file_niedodane.write(dodaj)
                        file_niedodane.close

    if not custom_list:
        tabPage.put(tabOutput, 'aktualizacja')

    if custom_list and filename and kategorie[0].buffer != '':
        file_words = open(filename, 'w')
        kategorie[0].tabelka += '\n| [[%s%d|%d]]' % (kategorie[0].pages, kategorie[0].counter/wordsPerPage, kategorie[0].counter/wordsPerPage)
        file_words.write(kategorie[0].buffer)
        if not offline_mode:
            outputPage.put(kategorie[0].buffer, comment='hasła zaimportowane z sjp.pl')
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
