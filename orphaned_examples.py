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
from klasa import *

def extract_one_sentence(nkjp_match, nkjp_query):
    """
    NKJP matches return the matched word itself, plus its context on both
    sides. This function attempts to take all three (left, match, right)
    and extract one sentence.


    Args:
        nkjp_match (lxml.etree._Element): one result of NKJP api request,
            i.e. the content within one <line> tag
        nkjp_query (str): the base form that we were looking for, to create
            a wikilink for the matched word

    Returns:
        tuple: three strings: the left side of the NKJP match, the match
            itself (in [[baseform|match]] form) and the right side
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
    
    return (left_end_sentence.group(1).lstrip(), '[[{0}|{1}]]'.format(nkjp_query, centre), right_end_sentence.group(1) + right_end_sentence.group(2))

def wikitext_one_sentence(left_match_right):
    """
    Take a tuple with the left and right side of the matched word
    and format it for printing. This is a way to circumvent doing
    wikilink('[[word]]'), which doesn't work properly as of 01/2015

    Args:
        left_match_right (tuple): a tuple of three strings: the left side
            of the NKJP match, the match itself (in [[baseform|match]] form)
            and the right side

    Returns:
        str: [[the|The]] [[input]] [[sentence]] [[format]]ted [[like]] [[this]].
    """

    re_whitespace_left = re.compile(r'(\s*?)$')
    re_whitespace_right = re.compile(r'^(\s*)')

    whitespaces_left = re.search(re_whitespace_left, left_match_right[0])
    whitespaces_right = re.search(re_whitespace_right, left_match_right[2])

    pretty_sentence = wikilink(left_match_right[0])
    if whitespaces_left:
        pretty_sentence += whitespaces_left.group(1)
    pretty_sentence += left_match_right[1]
    if whitespaces_right:
        pretty_sentence += whitespaces_right.group(1)
    pretty_sentence += wikilink(left_match_right[2])

    return pretty_sentence

def get_reference(api_output):
    """
    Take one result from NKJP api (within <line> tags), extract info
    about autorship and format it for printing

    Args:
        api_output (lxml.etree._Element): one result of NKJP api request,
            i.e. the content within one <line> tag

    Returns:
        str: pretty formated citation
    """

    ref = 'Nazwisko Autora'
    
    # article title exists for newspaper records
    article_title = api_output.find('title_a')
    if article_title is not None and len(article_title.text) > 0:
        ref += ', \'\'{0}\'\''.format(article_title.text)

    # this is a book title or a newspaper name
    pub_title = api_output.find('title_mono')
    if pub_title is not None:
        ref += ', '
        if article_title is None:
            ref += '\'\''
        ref += pub_title.text.strip()
        if article_title is None:
            ref += '\'\''
    
    pub_date = api_output.find('pubDate')
    if pub_date is not None:
        ref += ', '
        if len(pub_date.text) == 8:
            ref += '{0}/{1}/'.format(pub_date.text[6:], pub_date.text[4:6])
        if len(pub_date.text) in (4, 8):
            ref += pub_date.text[:4]

    return ref

def get_definitions(word):
    """
    Load a page from pl.wikt and find all definitions in the Polish section.
    This can be used to show the user a list of definitions beside an example,
    so they can match the two.

    Args:
        word (str): page title on pl.wikt
    Returns:
        list: all definitions found in page, e.g. [('1.1', 'mean1'),
            ('1.2', 'mean2'), ('2.1', 'mean3')]
    """

    re_numbers = re.compile(r'\: \(([0-9]\.[0-9])\)\s*(.*)')

    try: wikipage = Haslo(word)
    except sectionsNotFound:
        pass
    else:
        if wikipage.type == 3:
            for langsection in wikipage.listLangs:
                if langsection.lang == 'polski':
                    langsection.pola()
                    for pos in langsection.znaczeniaDetail:
                        defs = re.findall(re_numbers, pos[1])
                        return defs

    return 0

def orphaned_examples():
    with open('output/porzucone.txt') as f, open('output/empty_sections.txt', 'r') as g:
        no_examples = g.read()
        for orphaned in f:
            if orphaned[3] == '-' or orphaned[-3] == '-':
                continue # let's skip prefixes and sufixes for now

            # words come in '*[[word]]' format hence the stripping below
            root = etree.parse(nkjp_lookup('{0}**'.format(orphaned[3:-3]))).getroot()
            #root = etree.parse(nkjp_lookup('a capite**'.format(orphaned[3:-3]))).getroot()
            #xmlout = nkjp_lookup('{0}**'.format(orphaned[3:-3])).read()
            #print(xml.dom.minidom.parseString(xmlout).toprettyxml())
            if root.find('concordance') is not None:
                found = 0
                for line in root.find('concordance').findall('line'):
                    sentence = extract_one_sentence(line, orphaned[3:-3])
                    for word in set(sentence[0].split() + sentence[2].split()):
                        lookup_word = morfAnalyse(word.strip('!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~'))[0]
                        if lookup_word and '\n{0}\n'.format(lookup_word) in no_examples:
                            print('orphan:', orphaned[3:-3])
                            print('missing example:', lookup_word)
                            print(sentence)
                            print(wikitext_one_sentence(sentence))
                            print(get_reference(line))
                            found = 1
                            break
                    #if found:
                    #    break
