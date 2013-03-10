#!/usr/bin/python
# -*- coding: utf-8 -*-

# szuka danego przez szukany_tekst wyrażenia w hasłach

import codecs
import catlib
import wikipedia
import pagegenerators
import re
import xmlreader
from klasa import *

def main():
	
	data = u'20120316'
	lista_stron2 = getListFromXML(data)
	
	re_nieprzechodni_dk_ndk1 = re.compile(ur'\'\'czasownik( (nie|)przechodni|)\'\' \({{ndk}} \'\'(\'(.*?)\'|brak)\'\', {{dk}} \'\'(\'(.*?)\'|brak)\'\'\)')
	re_zwrotny_dk_ndk1 = re.compile(ur'\'\'czasownik zwrotny\'\' \({{ndk}} \'\'(\'(.*?) (się|sobie)\'|brak)\'\', {{dk}} \'\'(\'(.*?) (się|sobie)\'|brak)\'\'\)')

	re_nieprzechodni_dk_ndk = re.compile(ur'\'\'czasownik( (nie|)przechodni|)\'\' \({{ndk}} \'\'(\'(.*?)\'|brak)\'\', {{dk}} \'\'(\'(.*?)\'|brak)\'\'\)$')
	re_zwrotny_dk_ndk = re.compile(ur'\'\'czasownik zwrotny\'\' \({{ndk}} \'\'(\'(.*?) (się|sobie)\'|brak)\'\', {{dk}} \'\'(\'(.*?) (się|sobie)\'|brak)\'\'\)$')
	
	ranking = []
	newlist = []
	#for line in t:
	#	ranking.append(line.strip())
	
	
	for a in lista_stron2:			
		#if int(a.revisionid) > 2646076 and a.username not in ('Olafbot', 'AlkamidBot', 'KamikazeBot', 'MastiBot', 'Luckas-bot', 'Agnese'):
		s1 = re.search(re_nieprzechodni_dk_ndk1, a.text)
		s2 = re.search(re_zwrotny_dk_ndk1, a.text)
		if s1 or s2:
			newlist.append(a.title)
	
	for a in newlist:
		try: h = Haslo(a)
		except sectionsNotFound:
			pass
		except WrongHeader:
			pass
		else:
			if h.type == 3:	
				changed = 0
				for elem in h.listLangs:
					if elem.lang == 'polski':
						elem.pola()
						if elem.type == 9:
							for pos in elem.znaczeniaDetail:
								s1 = re.search(re_nieprzechodni_dk_ndk, pos[0])
								s2 = re.search(re_zwrotny_dk_ndk, pos[0])
								if s1:
									group3 = s1.group(3).strip('\'')
									group5 = s1.group(5).strip('\'')

									if group3 == h.title:
										if group5 == 'brak':
											tmp = u'\'\'brak\'\''
										else:
											tmp = u'[[%s]]' % group5
										pos[0] = u'\'\'czasownik%s niedokonany\'\' ({{dk}} %s)' % (s1.group(1), tmp)
										elem.saveChanges()
										changed = 1
									elif group5 == h.title:
										if group3 == 'brak':
											tmp = u'\'\'brak\'\''
										else:
											tmp = u'[[%s]]' % group3
										pos[0] = u'\'\'czasownik%s dokonany\'\' ({{dk}} %s)' % (s1.group(1), tmp)
										elem.saveChanges()
										changed = 1
								elif s2:
									group1 = s2.group(1).strip('\'')
									group4 = s2.group(4).strip('\'')
									for e in s2.groups():
										print e
									if s2.group(2) == h.title:
										if group4 == 'brak':
											tmp = u'\'\'brak\'\''
										else:
											tmp = u'[[%s]]' % (group4)
										pos[0] = u'\'\'czasownik zwrotny niedokonany \'\'\'%s\'\'\'\'\' ({{dk}} %s)' % (group1, tmp)
										elem.saveChanges()
										changed = 1
									elif s2.group(5) == h.title:
										if group1 == 'brak':
											tmp = u'\'\'brak\'\''
										else:
											tmp = u'[[%s]]' % (group1)
										pos[0] = u'\'\'czasownik zwrotny dokonany \'\'\'%s\'\'\'\'\' ({{dk}} %s)' % (group4, tmp)
										elem.saveChanges()
										changed = 1
				if changed:
					h.push(False, myComment = u'ujednolicenie zapisu aspektów')
	
if __name__ == '__main__':
    try:
        main()
    finally:
        wikipedia.stopme()
