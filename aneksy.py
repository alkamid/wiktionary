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
	inp = codecs.open('lista_aneksy', encoding='utf-8')
	usun_poczatek = re.compile(u'(.*?)----', re.DOTALL)
	usun_liens = re.compile(u'({{Liens.*?\|(\s*|)mdl=[^}]*?}})', re.DOTALL)

	for line in inp:
		lista.append(line.split())
			
	for a in lista:
		page = pywikibot.Page(frwikt, u'Modèle:fr-conj-3-%s' % (a[0]))
		text = page.get()
		text_przed = u'<noinclude>[[Kategoria:Język francuski - szablony koniugacji|3-%s]] </noinclude>\n<noinclude>Koniugacja czasowników kończących się na \'\'\'\'\'-%s\'\'\'\'\' :\n:<nowiki>{{</nowiki>fr-koniugacja-3-%s | \'\'<prefiks>\'\' | \'\'<IPA prefiksu>\'\' | \'\'<parametry opcjonalne>\'\' }}\n*\'\'<prefiks>\'\' : to, co poprzedza \'\'-%s\'\'\n*\'\'<IPA prefiksu>\'\' : wymowa prefiksu w IPA.\n*\'\'<parametry dodatkowe>\'\' :\n**<code>\'=tak<code> jeśli słowo zaczyna się samogłoską\n**<code>aux-être=tak<code> jeśli posiłkowym czasownikiem jest [[être]]\n----' % (a[0], a[0], a[0], a[0])
		text = re.sub(usun_poczatek, u'', text)
		text = re.sub(usun_liens, u'', text)		
		text = re.sub(u'fr-conj', u'fr-koniugacja', text)
		text = re.sub(u'fr-koniugacja/Tableau', u'fr-koniugacja/Tabela', text)
		text = re.sub(u'fr-koniugacja/Tableau-composé', u'fr-koniugacja/Tabela-złożone', text)
		text = re.sub(u'gris', u'pogrub', text)
		text = re.sub(u'{{conj-fr-usuel', u'{{fr-koniugacja-zwyczajowe', text)
		text = re.sub(u'<noinclude>{{Documentation}}</noinclude>', u'', text)
		text = re.sub(u'\|(\s*|)cat={{{clé|{{{1|}}}}}}%s' % (a[0]), u'', text)
		text = re.sub(u'Conjugaison courante', u'Koniugacja powszechna', text)
		text = re.sub(u'Conjugaison alternative', u'Koniugacja alternatywna', text)
		final = text_przed + text
		print final

		filename = "szablony/fr-koniugacja-3-%s" % (a[0])

		file = open(filename, 'w')
		file.write(final.encode( "utf-8" ))
		file.close
	

if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
