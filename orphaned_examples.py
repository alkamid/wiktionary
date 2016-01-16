# -*- coding: utf-8 -*-

"""This script seeks to kill two birds with one stone: add examples of
usage to words that don't have them, and to include orphaned words in
these examples. It uses NKJP API (http://www.nkjp.uni.lodz.pl/help.jsp)
to fetch examples from the most comprehensive Polish language corpus.
"""

from nkjp_lookup import nkjp_lookup
from lxml import etree
import re
import string # for removing punctuation
from importsjp import morfAnalyse, wikilink
import xml.dom.minidom # for testing

def extract_one_sentence(nkjp_match, nkjp_query):
    """
    NKJP matches return the matched word itself, plus its context on both
    sides. This function attempts to take all three (left, match, right)
    and extract one sentence.
    """

    re_end_sentence_left = re.compile(r'.!?([^.?!]*?)$')
    re_end_sentence_right = re.compile(r'^([^.?!]*)(.)')
    left = nkjp_match.find('left').text
    centre = nkjp_match.find('match').text
    right = nkjp_match.find('right').text

    left_end_sentence = re.search(re_end_sentence_left, left)
    right_end_sentence = re.search(re_end_sentence_right, right)
    wikitext = ''
    if left_end_sentence:
        wikitext = left_end_sentence.group(1).lstrip()

    wikitext += '[[{0}|{1}]]'.format(nkjp_query, centre)
    
    if right_end_sentence:
        wikitext += right_end_sentence.group(1) + right_end_sentence.group(2)
    
    return wikitext

    

def orphaned_examples():
    with open('output/porzucone.txt') as f, open('output/empty_sections.txt', 'r') as g:
        no_examples = g.read()
        for orphaned in f:
            # words come in '*[[word]]' format hence the stripping below
            root = etree.parse(nkjp_lookup('{0}**'.format(orphaned[3:-3]))).getroot()
            #root = etree.parse(nkjp_lookup('a capite**'.format(orphaned[3:-3]))).getroot()
            #xmlout = nkjp_lookup('a** capite**').read()
            #print(xml.dom.minidom.parseString(xmlout).toprettyxml())
            if root.find('concordance') is not None:
                found = 0
                for line in root.find('concordance').findall('line'):
                    sentence = extract_one_sentence(line, orphaned[3:-3])
                    for word in sentence.split():
                        lookup_word = morfAnalyse(word.strip('!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~'))[0]
                        if lookup_word and '\n{0}\n'.format(lookup_word) in no_examples:
                            print('orphan:', orphaned[3:-3])
                            print('missing example:', lookup_word)
                            print(sentence)
                            found = 1
                            break
                    #if found:
                    #    break
