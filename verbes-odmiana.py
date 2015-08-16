#!/usr/bin/python
# -*- coding: utf-8 -*-

# do eksportowania wszystkich słów z podanych języków

import sys
sys.path.append('/home/adam/pywiki/pywikipedia')
import codecs
from pywikibot import Category
import pywikibot
from pywikibot import pagegenerators
import re

def main():

    frwikt = pywikibot.getSite('fr', 'wiktionary')

    lista = []
    inp = codecs.open('lista_odmiana', encoding='utf-8')

    for line in inp:
        lista.append(line.split())

    for a in lista:
        f = codecs.open('wikt-listy/całość', encoding='utf=8')
        src = f.read()

        gerondif = re.search('(.*) # \'\'{{ims}} {{ter}} \(gérondif\) czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
        pp = re.search('(.*) # \'\'{{ims}} {{przesz}} \(participe passé\) czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
        p1s = re.search('(.*) # \'\'1\. {{os}} {{lp}} {{ter}} trybu oznajmującego czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
        p2s = re.search('(.*) # \'\'2\. {{os}} {{lp}} {{ter}} trybu oznajmującego czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
        p3s = re.search('(.*) # \'\'3\. {{os}} {{lp}} {{ter}} trybu oznajmującego czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
        p1p = re.search('(.*) # \'\'1\. {{os}} {{lm}} {{ter}} trybu oznajmującego czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
        p2p = re.search('(.*) # \'\'2\. {{os}} {{lm}} {{ter}} trybu oznajmującego czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
        p3p = re.search('(.*) # \'\'3\. {{os}} {{lm}} {{ter}} trybu oznajmującego czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
        f1s = re.search('(.*) # \'\'1\. {{os}} {{lp}} {{przysz}} czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
        f2s = re.search('(.*) # \'\'2\. {{os}} {{lp}} {{przysz}} czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
        f3s = re.search('(.*) # \'\'3\. {{os}} {{lp}} {{przysz}} czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
        f1p = re.search('(.*) # \'\'1\. {{os}} {{lm}} {{przysz}} czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
        f2p = re.search('(.*) # \'\'2\. {{os}} {{lm}} {{przysz}} czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
        f3p = re.search('(.*) # \'\'3\. {{os}} {{lm}} {{przysz}} czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
        s1s = re.search('(.*) # \'\'1\. {{os}} {{lp}} {{ter}} trybu subjonctif czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
        s2s = re.search('(.*) # \'\'2\. {{os}} {{lp}} {{ter}} trybu subjonctif czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
        s3s = re.search('(.*) # \'\'3\. {{os}} {{lp}} {{ter}} trybu subjonctif czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
        s1p = re.search('(.*) # \'\'1\. {{os}} {{lm}} {{ter}} trybu subjonctif czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
        s2p = re.search('(.*) # \'\'2\. {{os}} {{lm}} {{ter}} trybu subjonctif czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)
        s3p = re.search('(.*) # \'\'3\. {{os}} {{lm}} {{ter}} trybu subjonctif czasownika\'\' \[\[%s#fr\|%s\]\]' % (a[0], a[0]), src)


        try: a[1]
        except IndexError:
            odmiana = '{{ims}} ' + gerondif.group(1) + ' • {{przesz}} '
            odmiana = odmiana + '(avoir) '
            odmiana = odmiana + pp.group(1) + ' • {{ter}} je ' + p1s.group(1) + ', tu ' + p2s.group(1) + ', il ' + p3s.group(1) + ', nous ' + p1p.group(1) + ', vous ' + p2p.group(1) + ', ils ' + p3p.group(1) + ' • {{przysz}} ' + f1s.group(1) + ', tu ' + f2s.group(1) + ', il ' + f3s.group(1) + ', nous ' + f1p.group(1) + ', vous ' + f2p.group(1) + ', ils ' + f3p.group(1) + ' • \'\'subjonctif\'\' je ' + s1s.group(1) + ', tu ' + s2s.group(1) + ', il ' + s3s.group(1) + ', nous ' + s1p.group(1) + ', vous ' + s2p.group(1) + ', ils ' + s3p.group(1) + ' • {{koniugacjaFRlink|' + a[0] + '}}'
            print(odmiana)
        else:
            try: a[2]
            except IndexError:
                odmiana = '{{ims}} ' + gerondif.group(1) + ' • {{przesz}} '
                odmiana = odmiana + '(être) '
                odmiana = odmiana + pp.group(1) + ' • {{ter}} je ' + p1s.group(1) + ', tu ' + p2s.group(1) + ', il ' + p3s.group(1) + ', nous ' + p1p.group(1) + ', vous ' + p2p.group(1) + ', ils ' + p3p.group(1) + ' • {{przysz}} ' + f1s.group(1) + ', tu ' + f2s.group(1) + ', il ' + f3s.group(1) + ', nous ' + f1p.group(1) + ', vous ' + f2p.group(1) + ', ils ' + f3p.group(1) + ' • \'\'subjonctif\'\' je ' + s1s.group(1) + ', tu ' + s2s.group(1) + ', il ' + s3s.group(1) + ', nous ' + s1p.group(1) + ', vous ' + s2p.group(1) + ', ils ' + s3p.group(1) + ' • {{koniugacjaFRlink|' + a[0] + '}}'
                print(odmiana)
            else:
                odmiana = '{{ims}} se ' + gerondif.group(1) + ' • {{przesz}} '
                odmiana = odmiana + '(s\'être) '
                odmiana = odmiana + pp.group(1) + ' • {{ter}} je me ' + p1s.group(1) + ', tu te ' + p2s.group(1) + ', il se ' + p3s.group(1) + ', nous nous ' + p1p.group(1) + ', vous vous ' + p2p.group(1) + ', ils se ' + p3p.group(1) + ' • {{przysz}} se ' + f1s.group(1) + ', tu te ' + f2s.group(1) + ', il se ' + f3s.group(1) + ', nous nous ' + f1p.group(1) + ', vous vous ' + f2p.group(1) + ', ils se ' + f3p.group(1) + ' • \'\'subjonctif\'\' je me ' + s1s.group(1) + ', tu te ' + s2s.group(1) + ', il se ' + s3s.group(1) + ', nous nous ' + s1p.group(1) + ', vous vous ' + s2p.group(1) + ', ils se ' + s3p.group(1) + ' • {{koniugacjaFRlink|' + a[0] + '}}'
                print(odmiana)




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
        pywikibot.stopme()
