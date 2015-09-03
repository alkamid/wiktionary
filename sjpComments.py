#!/usr/bin/python
# -*- coding: utf-8 -*-

# count comments in sjp.pl

import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import http.client
from lxml import etree, html

def main():
    ranking = []
    for i in range(3840):
        while True:
            try:
                web = html.parse('http://www.sjp.pl/slownik/lp.phtml?page=%d' % i)
            except IOError:
                return None
            break

        try: comments = web.xpath('//table[@class="ktb"]/tr/td[5]/text()')
        except AssertionError:
            return None
        try: words = web.xpath('//table[@class="ktb"]/tr/td[1]/a/text()')
        except AssertionError:
            return None

        if len(words) == len(comments):
            for j in range(len(words)):
                if int(comments[j])>10 and len(words[j])>2 and [words[j], int(comments[j])] not in ranking:
                    ranking.append([words[j], int(comments[j])])

    print(ranking)
    def sortkey(row):
        return float(row[1])

    ranking.sort(key=sortkey, reverse=True)
    text = ''
    for i in ranking:
        text += '\n%s=%d' % (i[0], i[1])

    file = open('output/sjpComments.txt', 'w')
    file.write(text.encode('utf-8'))
    file.close

if __name__ == '__main__':
    try:
        main()
    finally:
        pass
