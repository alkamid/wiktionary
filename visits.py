#!/usr/bin/python
# -*- coding: utf-8 -*-

'''This script counts page visits on the previous day. pagecounts files available from dumps.wikimedia.org are split in hours so this
is basically to sum data from 24 files, sort them in decreasing order and put on pl.wikt'''
import codecs
import os
import glob #need this to remove files
import subprocess
import wikipedia
import urllib
import urllib2
import datetime
import gzip
from operator import itemgetter

def checkSum(folder, filename, dateString):
	urlmd5 = 'http://dumps.wikimedia.org/other/pagecounts-raw/%s/%s-%s/md5sums.txt' % (dateString[:4], dateString[:4], dateString[4:6])
	md5 = urllib.urlopen(urlmd5)
	sum = None
	for line in md5:
		if filename in line:
			sum = line.split()[0]
	if sum:
		sumDownloaded = subprocess.check_output(["md5sum", folder+filename])[:32]
		if sum == sumDownloaded:
			return 1
		else:
			return 0
	else:
		return 0

def main():
	#get the default site - the bot is operating on pl.wikt only
	site = wikipedia.getSite()
	
	
	
	#a list and a dict to handle individual entries
	lista = []
	rankingDict = {}
	
	#control how many entries should appear on the stats site
	limitEntriesTo = 1000
	
	date_yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
	date_string = date_yesterday.strftime("%Y%m%d")
	data_slownie = date_string[6] + date_string[7] + '.' + date_string[4] + date_string[5] + '.' + date_string[0] + date_string[1] + date_string[2] + date_string[3]
	
	statSite = wikipedia.Page(site, u'Wikipedysta:AlkamidBot/statystyka/wizyty')
	
	for i in range(24):
		
		if i < 10:
			hour = '0%d' % i
		else:
			hour = '%d' % i
		for j in range(9):
			folder = '/mnt/user-store/alkamid/stats/'
			filename = 'pagecounts-%s-%s000%d.gz' % (date_string, hour, j)
			try: inp = gzip.open(folder + filename)
			except IOError:
				url = 'http://dumps.wikimedia.org/other/pagecounts-raw/%s/%s-%s/pagecounts-%s-%s000%d.gz' % (date_string[:4], date_string[:4], date_string[4:6], date_string, hour, j)
				while True:
					try: urllib2.urlopen(url)
					except urllib2.HTTPError:
						break
					else:
						urllib.urlretrieve(url, folder + filename)
						try: open(folder+filename)
						except IOError:
							break
						if checkSum(folder, filename, date_string):
							break
				try: inp = gzip.open(folder + filename)
				except IOError:
					pass
				else:
					break
			else:
				break
		
		try:
			for line in inp:
				#only process lines starting with "pl.d" which means pl.wiktionary
				if line[:4] == 'pl.d':
					
					#the lines should look like this: pl.d pagename visits size, where size is the size of the content returned
					a = line.split()
	
					#I don't know why, but the lines may differ in encoding, it is therefore necessary to check both encodings
					a[1] = urllib.unquote(a[1])
					try: a[1] = a[1].decode('string-escape').decode('utf-8')
					except UnicodeDecodeError:
						a[1] = a[1].decode('string-escape').decode('iso-8859-2')
					except ValueError:
						#this is to ignore ValueError: Trailing \ in string
						continue
	
					
					#if the page is not in the dictionary, add it with the initial count; if it is in dictionary, sum the visits
					try: rankingDict[a[1]]
					except KeyError:
						try: rankingDict[a[1]] = int(a[2])
						except ValueError:
							# if a[2] is not an integer, then there probably is a space in the pagename, which there shouldn't be, so just ignore these pages (they won't have significant count anyway)
							print u'The number of counts is not an integer! The entire line reads: "%s"' % line
					else:
						try: rankingDict[a[1]] += int(a[2])
						except ValueError:
							# if a[2] is not an integer, then there probably is a space in the pagename, which there shouldn't be, so just ignore these pages (they won't have significant count anyway
							print u'The number of counts is not an integer! The entire line reads: "%s"' % line
		except IOError:
			pass
		#print i - just for debugging, shows which hour we are in
		inp.close
	
	ranking = sorted(rankingDict.items(), key=itemgetter(1), reverse=True)

	text = u'Statystyka wizyt na stronach z %s. Nie obejmuje przestrzeni nazw: Plik, Szablon, Specjalna, Kategoria, Dyskusja Wikipedysty.' % data_slownie
	text += u'\n\n{| class="wikitable sortable"\n|-\n!strona\n!odwiedzin'
	textFile = u''

	i = 0
	for a in ranking:
		if (i<limitEntriesTo) and 'Plik:' not in a[0] and 'Szablon:' not in a[0] and 'Specjalna:' not in a[0] and 'Kategoria:' not in a[0] and 'Special:' not in a[0] and 'Dyskusja Wikipedysty:' not in a[0] and 'admin/' not in a[0]:
			textFile = textFile + u'\n%s|%d' % (a[0], a[1])
			text = text + u'\n|-\n|[[%s]]\n|%d' % (a[0], a[1])
			i += 1
			
	text += u'\n|}'
	text = text.replace(u'_', u' ')
	
	file = open("%s/wikt/moje/log/visits.txt" % os.environ['HOME'], 'w')
	file.write(textFile.encode('utf-8'))
	file.close
	
	statSite.put(text, comment = 'aktualizacja', botflag=False)
	
	#cleanup
	os.chdir('/mnt/user-store/alkamid/stats/')
	toRemove= glob.glob('pagecounts*.gz')
	for file in toRemove:
		os.remove(file)

if __name__ == '__main__':
    try:
        main()
    finally:
        wikipedia.stopme()
