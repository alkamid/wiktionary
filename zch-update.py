#!/usr/bin/python
# -*- coding: utf-8 -*-

import wikipedia
import catlib
import codecs
import pagegenerators
import re
from klasa import *
from os import environ
    
def retrieveEnPlusCommons(a):
    new = None
    
    han_char = re.compile(u'{{Han(_| )char\|(.*?)}', re.DOTALL)
    han_ref = re.compile(u'{{Han(_| )ref\|(.*})')
    zh_f = re.compile(u'{{zh-forms\|(.*?)}')
    hani_f = re.compile(u'{{Hani-forms\|(.*?)}')
    jap_f = re.compile(u'{{ja-forms\|(.*?)}')
    zh_hanzi_r = re.compile(ur'{{zh-hanzi\|(.*?)}')
    kx = re.compile(u'kx=(.*?)(\||})')
    dkj = re.compile(u'\|dkj=(.*?)(\||})')
    dj = re.compile(u'\|dj=(.*?)(\||})')
    hdz = re.compile(u'\|hdz=(.*?)(\||})')
    rn = re.compile(u'rn=([0-9]*?)\|')
    rad = re.compile(u'rad=(.)')
    han_as = re.compile(u'as=([0-9]*?)\|')
    sn = re.compile(u'sn=([0-9]*?)\|')
    canj = re.compile(u'canj=([^\|]*)')
    canjPars1 = re.compile(ur'(.*?)\([A-Z]*?\)')
    canjPars2 = re.compile(ur'.*?(\([A-Z]*?\))')
    cr = re.compile(u'four=(.*?)\|')
    alt = re.compile(u'alt=(.*?)\|')
    asj = re.compile(u'asj=(.*?)\|')
   
    rn_abort = 0
    rad_abort = 0
    han_as_abort = 0
    sn_abort = 0
    canj_abort = 0
    cr_abort = 0
   
    ang = wikipedia.Page(site_en, a)
    ang_text = ang.get()
    han_char_s = re.search(han_char, ang_text)
    
    new = NewChar(a)
    if han_char_s:
        szablon_han = han_char_s.group(2)
                         
        rn_s = re.search(rn, szablon_han)
        rad_s = re.search(rad, szablon_han)
        han_as_s = re.search(han_as, szablon_han)
        sn_s = re.search(sn, szablon_han)
        canj_s = re.search(canj, szablon_han)
        cr_s = re.search(cr, szablon_han)
        
        if rn_s == None or not rn_s.group(1).strip():
            #log = log + u'\n*[[%s]] - Nie istnieje argument \'rn\'' % a
            rn_abort = 1
        if rad_s == None or not rad_s.group(1).strip():
            #log = log + u'\n*[[%s]] - Nie istnieje argument \'rad\'' % a
            rad_abort = 1
        if han_as_s != None or not han_as_s.group(1).strip():
            if han_as_s.group(1) == u'0' or han_as_s.group(1) ==u'00':
                as_output = u'+ 0'
            else:
                if han_as_s.group(1)[0] == u'0':
                    as_output = u'+ %s' % han_as_s.group(1)[1]
                else:
                    as_output = u'+ %s' % han_as_s.group(1)
        else:
            han_as_abort = 1
            
        if not (rn_abort or rad_abort or han_as_abort):
            temp = u' %s %s %s' % (rn_s.group(1), rad_s.group(1), as_output)
            new.addKlucz(temp)
        if sn_s and sn_s.group(1).strip():
            new.addKreski(u' %s' % sn_s.group(1))
        if canj_s and canj_s.group(1).strip():
            separate1 = re.findall(canjPars1, canj_s.group(1))
            separate2 = re.findall(canjPars2, canj_s.group(1))
            cjzText = ''
            if len(separate1) == len(separate2):
                for c, d in zip(separate1, separate2):
                    cjzText = cjzText + c.replace(u'X', u'難') + d
            new.addCJZ(cjzText)
        if cr_s and cr_s.group(1).strip():
            new.addCR(cr_s.group(1))
            
        han_ref_s = re.search(han_ref, ang_text)
        if han_ref_s:
            kx_s = re.search(kx, han_ref_s.group(2))
            if kx_s:
                new.addSlownik('kx', kx_s.group(1))
            
            dkj_s = re.search(dkj, han_ref_s.group(2))
            if dkj_s:
                 new.addSlownik('dkj', dkj_s.group(1))
            
            dj_s = re.search(dj, han_ref_s.group(2))
            if dj_s:
                 new.addSlownik('dj', dj_s.group(1))
                
            hdz_s = re.search(hdz, han_ref_s.group(2))
            if hdz_s:
                 new.addSlownik('hdz', hdz_s.group(1))
        
        alt_s = re.search(alt, szablon_han)
        asj_s = re.search(asj, szablon_han)
        if alt_s and alt_s.group(1).strip():
            log(u'*[[%s]] - na en.wikt istnieje argument alt' % ang.title())
        if asj_s and asj_s.group(1).strip():
            log(u'*[[%s]] - na en.wikt istnieje argument asj' % ang.title())

    ku = u''
    xu = u''
    sou = u''
    sot = u''
    ming = u''
    upr = u''
    trad = u''
    shin = u''
    
    try: wikipedia.ImagePage(site_en, u'File:%s-clerical.svg' % a).fileIsOnCommons()
    except wikipedia.NoPage or wikipedia.IsRedirectPage:
        try: wikipedia.ImagePage(site_en, u'File:%s-clerical.png' % a).fileIsOnCommons()
        except wikipedia.NoPage or wikipedia.IsRedirectPage:
            try: wikipedia.ImagePage(site_en, u'File:%s-clerical.gif' % a).fileIsOnCommons()
            except wikipedia.NoPage:
                pass
            except wikipedia.IsRedirectPage:
                pass
            else:
                new.addWariant('c', '|g')
        else:
            new.addWariant('c', '|p')
    else:
        new.addWariant('c', '')             

    try: wikipedia.ImagePage(site_en, u'File:%s-xinshu.svg' % a).fileIsOnCommons()
    except wikipedia.NoPage or wikipedia.IsRedirectPage:
        try: wikipedia.ImagePage(site_en, u'File:%s-xinshu.png' % a).fileIsOnCommons()
        except wikipedia.NoPage or wikipedia.IsRedirectPage:
            try: wikipedia.ImagePage(site_en, u'File:%s-xinshu.gif' % a).fileIsOnCommons()
            except wikipedia.NoPage:
                pass
            except wikipedia.IsRedirectPage:
                pass
            else:
                new.addWariant('xt', '|g')
        else:
            new.addWariant('xt', '|p')
    else:
        new.addWariant('xt', '')      

    try: wikipedia.ImagePage(site_en, u'File:%s-still.svg' % a).fileIsOnCommons()
    except wikipedia.NoPage or wikipedia.IsRedirectPage:
        try: wikipedia.ImagePage(site_en, u'File:%s-caoshu.svg' % a).fileIsOnCommons()
        except wikipedia.NoPage or wikipedia.IsRedirectPage:
            try: wikipedia.ImagePage(site_en, u'File:%s-still.png' % a).fileIsOnCommons()
            except wikipedia.NoPage or wikipedia.IsRedirectPage:
                try: wikipedia.ImagePage(site_en, u'File:%s-caoshu.png' % a).fileIsOnCommons()
                except wikipedia.NoPage or wikipedia.IsRedirectPage:
                    try: wikipedia.ImagePage(site_en, u'File:%s-still.gif' % a).fileIsOnCommons()
                    except wikipedia.NoPage or wikipedia.IsRedirectPage:
                        try: wikipedia.ImagePage(site_en, u'File:%s-caoshu.gif' % a).fileIsOnCommons()
                        except wikipedia.NoPage:
                            pass
                        except wikipedia.IsRedirectPage:
                            pass
                        else:
                            new.addWariant('ca', '|g')
                    else:
                        new.addWariant('st', '|g')
                else:
                    new.addWariant('ca', '|p')
            else:
                new.addWariant('st', '|p')
        else:
            new.addWariant('ca', '')
    else:
        new.addWariant('st', '') 

                                    
    try: wikipedia.ImagePage(site_en, u'File:%s-kaishu.svg' % a).fileIsOnCommons()
    except wikipedia.NoPage or wikipedia.IsRedirectPage:
        try: wikipedia.ImagePage(site_en, u'File:%s-kaishu.png' % a).fileIsOnCommons()
        except wikipedia.NoPage or wikipedia.IsRedirectPage:
            try: wikipedia.ImagePage(site_en, u'File:%s-kaishu.gif' % a).fileIsOnCommons()
            except wikipedia.NoPage:
                pass
            except wikipedia.IsRedirectPage:
                pass
            else:
                new.addWariant('kt', '|g')
        else:
            new.addWariant('kt', '|p')
    else:
        new.addWariant('kt', '')    

    try: wikipedia.ImagePage(site_en, u'File:%s-songti.svg' % a).fileIsOnCommons()
    except wikipedia.NoPage or wikipedia.IsRedirectPage:
        try: wikipedia.ImagePage(site_en, u'File:%s-songti.png' % a).fileIsOnCommons()
        except wikipedia.NoPage or wikipedia.IsRedirectPage:
            try: wikipedia.ImagePage(site_en, u'File:%s-songti.gif' % a).fileIsOnCommons()
            except wikipedia.NoPage:
                pass
            except wikipedia.IsRedirectPage:
                pass
            else:
                new.addWariant('sot', '|g')
        else:
            new.addWariant('sot', '|p')
    else:
        new.addWariant('sot', '')
        
    try: wikipedia.ImagePage(site_en, u'File:%s-bw.png' % a).fileIsOnCommons()
    except wikipedia.NoPage or wikipedia.IsRedirectPage:
        try: wikipedia.ImagePage(site_en, u'File:%s-red.png' % a).fileIsOnCommons()
        except wikipedia.NoPage or wikipedia.IsRedirectPage:
            try: wikipedia.ImagePage(site_en, u'File:%s-order.gif' % a).fileIsOnCommons()
            except wikipedia.NoPage:
                pass
            except wikipedia.IsRedirectPage:
                pass
            else:
                try: tmpget = wikipedia.ImagePage(commons, u'File:%s-order.gif' % a).get()
                except wikipedia.NoPage or wikipedia.IsRedirectPage:
                    pass
                except wikipedia.IsRedirectPage:
                    pass
                else:
                    if not '{{ARlicense' in tmpget:
                        new.addKolejnosc('', u'{{zch-animacja')
        else:
            new.addKolejnosc('', u'{{zch-cienie')
    else:
        new.addKolejnosc('', u'{{zch-komiks')
                    
    try: wikipedia.ImagePage(site_en, u'File:%s-jbw.png' % a).fileIsOnCommons()
    except wikipedia.NoPage or wikipedia.IsRedirectPage:
        try: wikipedia.ImagePage(site_en, u'File:%s-jred.png' % a).fileIsOnCommons()
        except wikipedia.NoPage or wikipedia.IsRedirectPage:
            try: wikipedia.ImagePage(site_en, u'File:%s-jorder.gif' % a).fileIsOnCommons()
            except wikipedia.NoPage:
                pass
            except wikipedia.IsRedirectPage:
                pass
            else:
                try: tmpget = wikipedia.ImagePage(commons, u'File:%s-jorder.gif' % a).get()
                except wikipedia.NoPage or wikipedia.IsRedirectPage:
                    pass
                except wikipedia.IsRedirectPage:
                    pass
                else:
                    if not '{{ARlicense' in tmpget:
                        new.addKolejnosc('j', u'{{zch-animacja')
        else:
            new.addKolejnosc('j', u'{{zch-cienie')
    else:
        new.addKolejnosc('j', u'{{zch-komiks')  
    
    try: wikipedia.ImagePage(site_en, u'File:%s-tbw.png' % a).fileIsOnCommons()
    except wikipedia.NoPage or wikipedia.IsRedirectPage:
        try: wikipedia.ImagePage(site_en, u'File:%s-tred.png' % a).fileIsOnCommons()
        except wikipedia.NoPage or wikipedia.IsRedirectPage:
            try: wikipedia.ImagePage(site_en, u'File:%s-torder.gif' % a).fileIsOnCommons()
            except wikipedia.NoPage:
                pass
            except wikipedia.IsRedirectPage:
                pass
            else:
                try: tmpget = wikipedia.ImagePage(commons, u'File:%s-torder.gif' % a).get()
                except wikipedia.NoPage or wikipedia.IsRedirectPage:
                    pass
                except wikipedia.IsRedirectPage:
                    pass
                else:
                    if not '{{ARlicense' in tmpget:
                        new.addKolejnosc('t', u'{{zch-animacja')
        else:
            new.addKolejnosc('t', u'{{zch-cienie')
    else:
        new.addKolejnosc('t', u'{{zch-komiks')       
        
    try: wikipedia.ImagePage(site_en, u'File:%s-abw.png' % a).fileIsOnCommons()
    except wikipedia.NoPage or wikipedia.IsRedirectPage:
        try: wikipedia.ImagePage(site_en, u'File:%s-ared.png' % a).fileIsOnCommons()
        except wikipedia.NoPage or wikipedia.IsRedirectPage:
            try: wikipedia.ImagePage(site_en, u'File:%s-aorder.gif' % a).fileIsOnCommons()
            except wikipedia.NoPage:
                pass
            except wikipedia.IsRedirectPage:
                pass
            else:
                try: tmpget = wikipedia.ImagePage(commons, u'File:%s-aorder.gif' % a).get()
                except wikipedia.NoPage or wikipedia.IsRedirectPage:
                    pass
                except wikipedia.IsRedirectPage:
                    pass
                else:
                    if not '{{ARlicense' in tmpget:
                        new.addKolejnosc('a', u'{{zch-animacja')
        else:
            new.addKolejnosc('a', u'{{zch-cienie')
    else:
        new.addKolejnosc('a', u'{{zch-komiks')
        
    try: wikipedia.ImagePage(site_en, u'File:%s-oracle.svg' % a).fileIsOnCommons()
    except wikipedia.NoPage or wikipedia.IsRedirectPage:
        try: wikipedia.ImagePage(site_en, u'File:%s-oracle.png' % a).fileIsOnCommons()
        except wikipedia.NoPage:
            pass
        except wikipedia.IsRedirectPage:
            pass
        else:
            new.addEtym('o', u'%s|p' % a)
    else:
        new.addEtym('o', u'%s' % a)
    

    try: wikipedia.ImagePage(site_en, u'File:%s-bronze.svg' % a).fileIsOnCommons()
    except wikipedia.NoPage or wikipedia.IsRedirectPage:
        try: wikipedia.ImagePage(site_en, u'File:%s-bronze.png' % a).fileIsOnCommons()
        except wikipedia.NoPage:
            pass
        except wikipedia.IsRedirectPage:
            pass
        else:
            new.addEtym('br', u'%s|p' % a)
    else:
        new.addEtym('br', u'%s' % a)
        
    try: wikipedia.ImagePage(site_en, u'File:%s-bigseal.svg' % a).fileIsOnCommons()
    except wikipedia.NoPage or wikipedia.IsRedirectPage:
        try: wikipedia.ImagePage(site_en, u'File:%s-bigseal.png' % a).fileIsOnCommons()
        except wikipedia.NoPage:
            pass
        except wikipedia.IsRedirectPage:
            pass
        else:
            new.addEtym('bs', u'%s|p' % a)
    else:
        new.addEtym('bs', u'%s' % a)
    
    try: wikipedia.ImagePage(site_en, u'File:%s-seal.svg' % a).fileIsOnCommons()
    except wikipedia.NoPage or wikipedia.IsRedirectPage:
        try: wikipedia.ImagePage(site_en, u'File:%s-seal.png' % a).fileIsOnCommons()
        except wikipedia.NoPage:
            pass
        except wikipedia.IsRedirectPage:
            pass
        else:
            new.addEtym('ss', u'%s|p' % a)
    else:
        new.addEtym('ss', u'%s' % a)
    
    zh_f_s = re.search(zh_f, ang_text)    
    ja_f_s = re.search(jap_f, ang_text)
    hani_f_s = re.search(hani_f, ang_text)
    zh_hanzi_s = re.search(zh_hanzi_r, ang_text)
    
    if ja_f_s:
        ja_f_str = ja_f_s.group(1).replace("[","").replace("]","").replace("{{zh-lookup|", "").replace("}", "")
        ja_osobno = ja_f_str.split('|')

        try: new.addWariant('ct', ja_osobno[2])
        except IndexError:
            log(u'*[[%s]] - nietypowy zapis wariantów tradycyjnych/uproszczonych na en.wikt' % a)
        try: new.addWariant('cu', ja_osobno[1])
        except IndexError:
            log(u'*[[%s]] - nietypowy zapis wariantów tradycyjnych/uproszczonych na en.wikt' % a)
        try: new.addWariant('js', ja_osobno[0])
        except IndexError:
            log(u'*[[%s]] - nietypowy zapis wariantów tradycyjnych/uproszczonych na en.wikt' % a)
    elif zh_f_s:
        zh_f_str = zh_f_s.group(1).replace("[","").replace("]","").replace("{{zh-lookup|", "").replace("}", "")
        zh_osobno = zh_f_str.split('|')
        new.addWariant('ct', zh_osobno[1])
        new.addWariant('cu', zh_osobno[0])
    elif hani_f_s:
        hani_f_str = hani_f_s.group(1).replace("[","").replace("]","").replace("{{zh-lookup|", "").replace("}", "")
        hani_osobno = hani_f_str.split('|')
        try: new.addWariant('ct', hani_osobno[1])
        except IndexError:
            log(u'*[[%s]] - nietypowy zapis wariantów tradycyjnych/uproszczonych na en.wikt' % a)
        try: new.addWariant('cu', hani_osobno[0])
        except IndexError:
            log(u'*[[%s]] - nietypowy zapis wariantów tradycyjnych/uproszczonych na en.wikt' % a)
    elif zh_hanzi_s:
        zh_hanzi_str = zh_hanzi_s.group(1).replace("[","").replace("]","").replace("{{zh-lookup|", "").replace("}", "")
        new.addWariant('ct', zh_hanzi_str)
        new.addWariant('cu', zh_hanzi_str)
        
    
        
    return new

def ordinal(pl):
    if not pl.kody.dict.has_key('u') or pl.kody.dict['u'].strip() == '':
        pl.kody.dict['u'] = hex(ord(pl.title))[2:]
        pl.saveChanges()
        return 1
    return 0

def compare(en, pl, pole, SimpTrad=666): #a function that compares two fields - for each field there's a different method for comparison. If neither value is empty and if they are different it's written in the log. If pl.wikt field is empty and en.wikt is not, then the Polish one is updated.
    
    if pole == u'klucz':
        if pl.klucz.text.strip():
            if en.klucz != pl.klucz.text:
                log(u'*[[%s]] - różnica między en.wikt i pl.wikt w parametrze "klucz"' % (en.title))
             
        elif en.klucz.strip():
            pl.klucz.text = en.klucz
            pl.saveChanges()
            return 1
    if pole == u'kreski':
        if pl.kreski.text.strip():
            if en.kreski.strip() != pl.kreski.text.strip():
                log(u'*[[%s]] - różnica między en.wikt i pl.wikt w parametrze "kreski"' % (en.title))
                
        elif en.kreski.strip():
            pl.kreski.text = en.kreski
            pl.saveChanges()
            return 1
    if pole in ('kody', 'slowniki', 'warianty', 'kolejnosc', 'etymologia'):
        try: enAttr = getattr(en, pole)
        except AttributeError:
            return 0
        
        try: plAttr = getattr(pl, pole)
        except AttributeError:
            return 0

        if pole == 'kody':
            keyset = ('cjz', 'cr')
        elif pole == 'slowniki':
            keyset = ('kx', 'dkj', 'dj', 'hdz')
        elif pole == 'warianty':
            keyset = ('c', 'xt', 'ca', 'kt', 'sot')
        elif pole == 'kolejnosc':
            keyset = ('', 'j', 't', 'a')
        elif pole == 'etymologia':
            keyset = ('o', 'br', 'bs', 'ss')
        
        done = 0
        change = 0

        for key in keyset:
            try: enAttr[key]
            except KeyError:
                pass
            else:              
                try: plAttr.dict[key]
                except KeyError:
                    change = 1
                else:
                    if plAttr.dict[key].strip() != enAttr[key].strip():
                        if pole in ('warianty', 'kolejnosc', 'etymologia'):
                            change = 1
                        elif pole in ('kody', 'slowniki'):
                            if not plAttr.dict[key].strip():
                                change = 1
                            else:
                                if 'X' in plAttr.dict[key]:
                                    change = 1
                                else:
                                    log(u'*[[%s]] - różnica między en.wikt i pl.wikt w parametrze %s/%s' % (en.title, pole, key))
                        else:
                            log(u'*[[%s]] - różnica między en.wikt i pl.wikt w parametrze %s/%s' % (en.title, pole, key))
                if change:
                    plAttr.dict[key] = enAttr[key]
                    pl.saveChanges()
                    done = 1
        if done:
            return 1

    if pole == u'upr-trad':
        keyset = ('cu', 'ct', 'js')
        try: en.warianty
        except AttributeError:
            return 0
        
        try: pl.warianty.dict
        except AttributeError:
            return 0
        
        done = 0
        change = 0
        
        for key in keyset:
            try: en.warianty[key]
            except KeyError:
                try: SimpTrad.warianty[key]
                except KeyError:
                    pass
                else:
                    try: pl.warianty.dict[key]
                    except KeyError:
                        pl.warianty.dict[key] = SimpTrad.warianty[key]
                        change = 1
                    else:
                        if sorted(pl.warianty.dict[key]) == sorted(SimpTrad.warianty[key]):
                            pass
                        else:
                            log(u'*[[%s]] - upr/trad różnią się na pl.wikt i w tabeli' % pl.title)
                    
            else:              
                try: SimpTrad.warianty[key]
                except KeyError:
                    try: pl.warianty.dict[key]
                    except KeyError:
                        pl.warianty.dict[key] = en.warianty[key]
                        change = 1
                    else:
                        if sorted(pl.warianty.dict[key]) == sorted(en.warianty[key]):
                            pass
                        else:
                            log(u'*[[%s]] - upr/trad różnią się na pl.wikt i en.wikt' % pl.title)
                else:
                    try: pl.warianty.dict[key]
                    except KeyError:
                        if sorted(SimpTrad.warianty[key]) == sorted(en.warianty[key]):
                            pl.warianty.dict[key] = en.warianty[key]
                            change = 1
                        else:
                            log(u'*[[%s]] - upr/trad różnią się na en.wikt i w tabeli' % pl.title)
                    else:
                        if sorted(pl.warianty.dict[key]) == sorted(en.warianty[key]) and set(SimpTrad.warianty[key]).issubset(pl.warianty.dict[key]):
                            pass
                        else:
                            log(u'*[[%s]] - upr/trad istnieją wszędzie (tabela, pl.wikt, en.wikt), ale się między sobą różnią' % pl.title)
    
        if change:
            pl.saveChanges()
            return 1
    
    return 0
            
class NewChar():
    def __init__(self, title):
        self.title = title
        self.klucz = u''
        self.kreski = u''
        self.kody = {}
        self.slowniki = {}
        self.kolejnosc = {}
        self.warianty = {}
        self.etymologia = {}
    def addKlucz(self, klucz):
        self.klucz = klucz
    def addKreski(self, kreski):
        self.kreski = kreski
    def addCJZ(self, cjz):
        self.kody['cjz'] = cjz
    def addCR(self, cr):
        self.kody['cr'] = cr
    def addSlownik(self, slownik, value):
        self.slowniki[slownik] = value
    def addWariant(self, wariant, value):
        if wariant in ('cu', 'ct', 'js'):
            if not self.warianty.has_key(wariant):
                self.warianty[wariant] = []
            if len(value) == 2:
                self.warianty[wariant].append(value[0])
                self.warianty[wariant].append(value[1])
            elif len(value) == 1:
                self.warianty[wariant].append(value)
            else:
                log(u'*[[%s]] - na en.wikt dziwny format wariantów (ct, cu, js)' % self.title)
        else:
            self.warianty[wariant] = self.title + value
    def addKolejnosc(self, kolejnosc, value):
        self.kolejnosc[kolejnosc] = value
    def addEtym(self, etym, value):
        self.etymologia[etym] = value

def makeConversionList():
    inp = codecs.open('%s/wikt/moje/input/utftable.txt' % environ['HOME'], encoding='utf-8')
    list = [{}, {}]
    for line in inp:
        if not list[0].has_key(line[0]):
            list[0][line[0]] = []
        list[0][line[0]].append(line[2])
        if not list[1].has_key(line[1]):
            list[1][line[2]] = []
        list[1][line[2]].append(line[0])

    return list

class SimpTrad():
    def __init__(self, title, table):
        self.title = title
        self.warianty = {}
        if table[0].has_key(title):
            self.warianty['ct'] = table[0][title]
            self.warianty['cu'] = title
        elif table[1].has_key(title):
            self.warianty['cu'] = table[1][title]
            self.warianty['ct'] = title

def log(text):
    if test_mode == 1:
        print text
    else:
        if text != u'':
            file = open("%s/wikt/moje/log/zch.txt" % environ['HOME'], 'a')
            file.write (('\n' + text).encode("utf-8"))
            file.close

def main():
    
    list = makeConversionList()
    global site_pl
    site_pl = wikipedia.getSite()
    global site_en
    site_en = wikipedia.getSite('en', 'wiktionary')
    global commons
    commons = wikipedia.getSite('commons', 'commons')
    global test_mode
    test_mode = 0
    global data_en
    data_en = '20120125'
    cat_en = catlib.Category(site_en, u'Category:Han_characters')
    lista_stron_en = pagegenerators.CategorizedPageGenerator(cat_en)
    
    file = open("%s/wikt/moje/log/zch.txt" % environ['HOME'], 'w')
    file.write(''.encode("utf-8"))
    file.close
    
    #pagesDump1 = xmlreader.XmlDump('/mnt/user-store/dumps/enwiktionary/enwiktionary-%s-pages-articles.xml' % data_en)
    #pagesDump = xmlreader.XmlDump.parse(pagesDump1)
    
    lista_stron_en = [u'㭻']
    for elem in lista_stron_en:
        title = elem.title()
        if len(title) == 1:
            en = retrieveEnPlusCommons(title)
            pl = Haslo(title)
            sekcja = None
            if en and pl.type not in (0,1,2):
                try: pl.listLangs
                except AttributeError:
                    log(u'*[[%s]] - brak listy sekcji!' % en.title)
                else:
                    for sec in pl.listLangs:
                        if sec.lang == u'znak chiński':
                            sec.pola()
                            if sec.type == 4:
                                sekcja = sec
            elif en and pl.type == 1:               
                sekcja = Sekcja(title=title, type=4, lang=u'znak chiński')
                
                            
            if sekcja:    
                push = 0
                if compare(en, sekcja, u'klucz'):
                    push = 1
                if compare(en, sekcja, u'kreski'):
                    push = 1
                if compare(en, sekcja, u'kody'):
                    push = 1
                if compare(en, sekcja, u'warianty'):
                    push = 1
                if compare(en, sekcja, u'kolejnosc'):
                    push = 1
                if compare(en, sekcja, u'etymologia'):
                    push = 1
                if compare(en, sekcja, u'slowniki'):
                    push = 1
                if ordinal(sekcja):
                    push = 1
                    
                tab = SimpTrad(title, list)
                if compare(en, sekcja, u'upr-trad', tab):
                    push = 1
                if push:
                    if pl.type == 1:
                        pl = Haslo(title, new=True)
                        pl.addSection(sekcja)
                        log(u'*[[%s]] - dodano' % title)
                    
                    pl.push(False, myComment = u'aktualizacja danych o znaku chińskim; źródła: [[:en:%s]], http://simplify.codeplex.com/, commons' % title, new=True)

    logPage = wikipedia.Page(site_pl, u'Wikipedysta:AlkamidBot/listy/znak chiński')
    logPageText = u'AlkamidBot cyklicznie sprawdza, czy w angielskim Wikisłowniku lub na commons pojawiły się nowe informacje o znakach chińskich (np. warianty pisania, zapisy etymologiczne itp.). Na tej liście zapisuje problemy, jakie napotkał: ("tabela" oznacza dane z http://simplify.codeplex.com/)\n\n'
    file = codecs.open("%s/wikt/moje/log/zch.txt" % environ['HOME'], 'r', 'utf-8')
    logPageText += file.read()
    file.close
    #logPage.put(logPageText, comment=u'aktualizacja')

if __name__ == '__main__':
    try:
        main()
    finally:
        wikipedia.stopme()