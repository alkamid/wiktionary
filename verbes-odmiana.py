#!/usr/bin/python
# -*- coding: utf-8 -*-

# do eksportowania wszystkich słów z podanych języków

import sys
sys.path.append('/home/adam/pywiki/pywikipedia')
import codecs
import catlib
import wikipedia
import pagegenerators
import re

def main():
	
	frwikt = wikipedia.getSite('fr', 'wiktionary')
	
	lista = []
	inp = codecs.open('lista_odmiana', encoding='utf-8')

	for line in inp:
		lista.append(line.split())
			
	for a in lista:
		f = codecs.open(u'wikt-listy/całość', encoding='utf=8')
		src = f.read()

		gerondif = re.search(u'(.*) # \'\'{{ims}} {{ter}} \(gérondif\) czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
		pp = re.search(u'(.*) # \'\'{{ims}} {{przesz}} \(participe passé\) czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
		p1s = re.search(u'(.*) # \'\'1\. {{os}} {{lp}} {{ter}} trybu oznajmującego czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
		p2s = re.search(u'(.*) # \'\'2\. {{os}} {{lp}} {{ter}} trybu oznajmującego czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
		p3s = re.search(u'(.*) # \'\'3\. {{os}} {{lp}} {{ter}} trybu oznajmującego czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
		p1p = re.search(u'(.*) # \'\'1\. {{os}} {{lm}} {{ter}} trybu oznajmującego czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
		p2p = re.search(u'(.*) # \'\'2\. {{os}} {{lm}} {{ter}} trybu oznajmującego czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
		p3p = re.search(u'(.*) # \'\'3\. {{os}} {{lm}} {{ter}} trybu oznajmującego czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
		f1s = re.search(u'(.*) # \'\'1\. {{os}} {{lp}} {{przysz}} czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
		f2s = re.search(u'(.*) # \'\'2\. {{os}} {{lp}} {{przysz}} czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
		f3s = re.search(u'(.*) # \'\'3\. {{os}} {{lp}} {{przysz}} czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
		f1p = re.search(u'(.*) # \'\'1\. {{os}} {{lm}} {{przysz}} czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
		f2p = re.search(u'(.*) # \'\'2\. {{os}} {{lm}} {{przysz}} czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
		f3p = re.search(u'(.*) # \'\'3\. {{os}} {{lm}} {{przysz}} czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
		s1s = re.search(u'(.*) # \'\'1\. {{os}} {{lp}} {{ter}} trybu subjonctif czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
		s2s = re.search(u'(.*) # \'\'2\. {{os}} {{lp}} {{ter}} trybu subjonctif czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
		s3s = re.search(u'(.*) # \'\'3\. {{os}} {{lp}} {{ter}} trybu subjonctif czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
		s1p = re.search(u'(.*) # \'\'1\. {{os}} {{lm}} {{ter}} trybu subjonctif czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
		s2p = re.search(u'(.*) # \'\'2\. {{os}} {{lm}} {{ter}} trybu subjonctif czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
		s3p = re.search(u'(.*) # \'\'3\. {{os}} {{lm}} {{ter}} trybu subjonctif czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
		

		try: a[1]
		except IndexError:
			odmiana = u'{{ims}} ' + gerondif.group(1) + u' • {{przesz}} '
			odmiana = odmiana + u'(avoir) '
			odmiana = odmiana + pp.group(1) + u' • {{ter}} je ' + p1s.group(1) + u', tu ' + p2s.group(1) + u', il ' + p3s.group(1) + u', nous ' + p1p.group(1) + u', vous ' + p2p.group(1) + u', ils ' + p3p.group(1) + u' • {{przysz}} ' + f1s.group(1) + u', tu ' + f2s.group(1) + u', il ' + f3s.group(1) + u', nous ' + f1p.group(1) + u', vous ' + f2p.group(1) + u', ils ' + f3p.group(1) + u' • \'\'subjonctif\'\' je ' + s1s.group(1) + u', tu ' + s2s.group(1) + u', il ' + s3s.group(1) + u', nous ' + s1p.group(1) + u', vous ' + s2p.group(1) + u', ils ' + s3p.group(1) + u' • {{koniugacjaFRlink|' + a[0] + u'}}'
			print odmiana
		else:
			try: a[2]
			except IndexError:
				odmiana = u'{{ims}} ' + gerondif.group(1) + u' • {{przesz}} '
				odmiana = odmiana + u'(être) '
				odmiana = odmiana + pp.group(1) + u' • {{ter}} je ' + p1s.group(1) + u', tu ' + p2s.group(1) + u', il ' + p3s.group(1) + u', nous ' + p1p.group(1) + u', vous ' + p2p.group(1) + u', ils ' + p3p.group(1) + u' • {{przysz}} ' + f1s.group(1) + u', tu ' + f2s.group(1) + u', il ' + f3s.group(1) + u', nous ' + f1p.group(1) + u', vous ' + f2p.group(1) + u', ils ' + f3p.group(1) + u' • \'\'subjonctif\'\' je ' + s1s.group(1) + u', tu ' + s2s.group(1) + u', il ' + s3s.group(1) + u', nous ' + s1p.group(1) + u', vous ' + s2p.group(1) + u', ils ' + s3p.group(1) + u' • {{koniugacjaFRlink|' + a[0] + u'}}'
				print odmiana
			else:
				odmiana = u'{{ims}} se ' + gerondif.group(1) + u' • {{przesz}} '
				odmiana = odmiana + u'(s\'être) '
				odmiana = odmiana + pp.group(1) + u' • {{ter}} je me ' + p1s.group(1) + u', tu te ' + p2s.group(1) + u', il se ' + p3s.group(1) + u', nous nous ' + p1p.group(1) + u', vous vous ' + p2p.group(1) + u', ils se ' + p3p.group(1) + u' • {{przysz}} se ' + f1s.group(1) + u', tu te ' + f2s.group(1) + u', il se ' + f3s.group(1) + u', nous nous ' + f1p.group(1) + u', vous vous ' + f2p.group(1) + u', ils se ' + f3p.group(1) + u' • \'\'subjonctif\'\' je me ' + s1s.group(1) + u', tu te ' + s2s.group(1) + u', il se ' + s3s.group(1) + u', nous nous ' + s1p.group(1) + u', vous vous ' + s2p.group(1) + u', ils se ' + s3p.group(1) + u' • {{koniugacjaFRlink|' + a[0] + u'}}'
				print odmiana		

		
		

		'''
		filename = "szablony/fr-koniugacja-3-%s" % (a[0])

		file = open(filename, 'w')
		file.write(final.encode( "utf-8" ))
		file.close
		'''

if __name__ == '__main__':
    try:
        main()
    finally:
        wikipedia.stopme()
