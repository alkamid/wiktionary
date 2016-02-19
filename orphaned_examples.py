# -*- coding: utf-8 -*-

"""This script seeks to kill two birds with one stone: add examples of
usage to words that don't have them, and to include orphaned words in
these examples. It uses NKJP API (http://www.nkjp.uni.lodz.pl/help.jsp)
to fetch examples from the most comprehensive Polish language corpus.
"""

from nkjp_lookup import nkjp_lookup
from lxml import etree
import re
import json
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

    abbreviations = ['np\.', 'tzw\.', 'm\.in\.', 'prof\.', 'św\.', 'dr\.'] 

    # regex here: https://regex101.com/r/yB8vG7/6

    re_end_sentence_left = re.compile(r'(?:^|[.?!]\s*)((?:' + r'|'.join(abbreviations) + r'|[^.?!]|[.?!](?!\s*[A-Z]))+)$')
    re_end_sentence_right = re.compile(r'^((?:' + r'|'.join(abbreviations) + r'|[^.?!]|[.?!](?!\s*[A-Z])|)+(?:[.?!]|$))')
    #print(r'^((?:' + r'|'.join(abbreviations) + r'|[^.?!]|[.?!](?!\s*[A-Z])|)+(?:[.?!]|$))')

    left = nkjp_match.find('left').text
    centre = nkjp_match.find('match').text
    right = nkjp_match.find('right').text

    right_end_sentence = re.search(re_end_sentence_right, right)


    left_return = ''

    # Usually the context is to the left of the matched word, so it
    # might be useful to set the lower limit for the length of the left context
    left_context_min_length = 100

    while len(left_return) < left_context_min_length:
        left_end_sentence = re.search(re_end_sentence_left, left)
        if left_end_sentence:
            left_return = left_end_sentence.group(1) + left_return
            left = left.replace(left_end_sentence.group(1), '')
        else:
            break


    # cut some extra stuff on the left so users can add it
    left_extra = ''
    if len(left_return) >= left_context_min_length:
        while len(left_extra) < left_context_min_length:
            left_extra_end_sentence = re.search(re_end_sentence_left, left)
            if left_extra_end_sentence:
                left_extra = left_extra_end_sentence.group(1) + left_extra
                left = left.replace(left_extra_end_sentence.group(1), '')
            else:
                break
            
    
    centre_return = '[[{0}|{1}]]'.format(nkjp_query, centre)
    
    if right_end_sentence:
        right_return = right_end_sentence.group(1)
    else:
        right_return = ''
    
    #print((left_return, centre, right_return))
    return (left_return, centre, right_return, left_extra)

def check_sentence_quality(left_match_right):
    """
    Take a tuble with the left and right side of the matched word
    and check a few arbitrary conditions to determine whether it's
    a good example or not

    Args:
        left_match_right (tuple): a tuple of three strings: the left side
            of the NKJP match, the match itself (in [[baseform|match]] form)
            and the right side

    Returns:
        int: 0 for bad quality, 1 for good quality
    """

    joined_sentence = ''.join(left_match_right[:3])

    # the proportion of upper case letters to all letters is too high
    allowed_uppercase_proportion = 0.1

    if sum(1 for c in joined_sentence if c.isupper())/len(joined_sentence) > allowed_uppercase_proportion:
        return 0

    # the sentence is too long
    allowed_length = 500

    if len(joined_sentence) > allowed_length:
        return 0

    # there are too many newlines (most likely a list)
    allowed_newlines = 3
    
    if joined_sentence.count('\n') > allowed_newlines:
        return 0



def wikitext_one_sentence(left_match_right, match_base_form):
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

    # https://regex101.com/r/yB6tQ8/3
    re_punctuation_around = re.compile(r'([\W]*?)([\w]+(?:(?:-|\s)\w+)*)([\W]*)')

    whitespaces_left = re.search(re_whitespace_left, left_match_right[0])
    whitespaces_right = re.search(re_whitespace_right, left_match_right[2])
    punctuation_match = re.search(re_punctuation_around, left_match_right[1])

    pretty_sentence = wikilink(left_match_right[0])
    if whitespaces_left:
        pretty_sentence += whitespaces_left.group(1)

    if punctuation_match:
        pretty_sentence += punctuation_match.group(1) + '[[' + match_base_form
        if match_base_form != punctuation_match.group(2):
            pretty_sentence += '|' + punctuation_match.group(2)
        pretty_sentence += ']]' + punctuation_match.group(3)

    else:
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
        str: pretty formated citation. If the source is on the blacklist,
            returns ''
    """

    ref = 'Nazwisko Autora'

    match = api_output.find('match').text.lower()
    
    excluded_titles = ['Wikipedia:']

    # article title exists for newspaper records
    article_title = api_output.find('title_a')
    if article_title is not None:
        if any(article_title.text.startswith(c) for c in excluded_titles):
            return ''
        elif len(article_title.text) > 0:
            ref += ', \'\'{0}\'\''.format(article_title.text)



    # this is a book title or a newspaper name
    pub_title = api_output.find('title_mono')
    if pub_title is not None:
        if article_title.text.lower().startswith(match) and 'Wikipedia' in pub_title.text:
            return '' # Wikipedia pages about matched words are probably
            # the best examples
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
    re_refs = re.compile(r'(<ref.*?(?:/>|</ref>))')

    try: wikipage = Haslo(word)
    except sectionsNotFound:
        pass
    else:
        if wikipage.type == 3:
            for langsection in wikipage.listLangs:
                if langsection.lang == 'polski':
                    langsection.pola()
                    defs = []
                    for pos in langsection.znaczeniaDetail:
                        if word + ' się' in pos[0]:
                            prefix = '(' + word + ' się) '
                        else:
                            prefix = ''

                        defs_found = re.findall(re_numbers, pos[1])
                        print(defs_found)
                        # get rid of <refs> in definitions
                        defs += [(d[0], prefix + re.sub(re_refs, '', d[1])) for d in defs_found]
                        
                        # dewikify (remove [[ ]])
                        #defs = [(d[0], d[1].replace('[[', '').replace(']]', '')) for d in defs]
                    
                    return defs

    return 0


def get_definitions_new(word):
    """
    Load a page from pl.wikt and find all definitions in the Polish section.
    This can be used to show the user a list of definitions beside an example,
    so they can match the two.

    Args:
        word (str): page title on pl.wikt
    Returns:
        str: all definitions found in page along with their part of speech
            descriptions
    """

    # https://regex101.com/r/sX1yF7/1
    re_numbers = re.compile(r'\: \(([0-9]\.[0-9]{1,2})\)\s*.*')
    re_refs = re.compile(r'(<ref.*?(?:/>|</ref>))')

    try: wikipage = Haslo(word)
    except sectionsNotFound:
        pass
    else:
        if wikipage.type == 3:
            for langsection in wikipage.listLangs:
                if langsection.lang == 'polski':
                    langsection.pola()
                    nums = re.findall(re_numbers, langsection.subSections['znaczenia'].text)

                    return re.sub(re_refs, '', langsection.subSections['znaczenia'].text)

    return 0


def orphaned_examples(test_word=None):
    buffer_size = 20
    pages_count = 0
    output = []
    i = 0

    # this is a dirty trick, because morfAnalyse() and wikilink() don't
    # really work as they should. The following regex extracts the first part
    # of [[these|links]]
    re_base_form = re.compile(r'\[\[(.*?)(?:\||\]\])')

    with open('output/porzucone.txt') as f,\
    open('output/empty_sections.txt', 'r') as g:

        no_examples = g.read()
        if test_word:
            f = ['*[[{0}]]\n'.format(test_word)]
        for orphaned in f:
            print(orphaned)

            if len(output) == buffer_size:
                with open('output/json_examples_{0}.json'.format(pages_count), 'w') as o:
                    o.write(json.dumps(output, ensure_ascii=False, indent=4) + ',')
                    pages_count += 1
                    output = []
                    i = 0


            
            if orphaned[3] == '-' or orphaned[-3] == '-' \
               or orphaned[3].isupper():
                continue # let's skip prefixes and sufixes for now, also whatever starts with a capital leter


            # words come in '*[[word]]' format hence the stripping below
            root = etree.parse(nkjp_lookup('{0}**'.format(orphaned[3:-3]).replace(' ', '** '))).getroot()
            #root = etree.parse(nkjp_lookup('a capite**'.format(orphaned[3:-3]))).getroot()
            #xmlout = nkjp_lookup('{0}**'.format(orphaned[3:-3])).read()
            #print(xml.dom.minidom.parseString(xmlout).toprettyxml())
            if root.find('concordance') is not None:
                found = 0
                for line in root.find('concordance').findall('line'):
                    sentence = extract_one_sentence(line, orphaned[3:-3])
                    if check_sentence_quality(sentence) == 0:
                        continue
                    allwords = re.findall(re_base_form, wikilink(sentence[0] + sentence[2]))
                    for lookup_word in allwords:
                        if ' się' in lookup_word:
                            lookup_word = lookup_word[:-4]
                        if '\n{0}\n'.format(lookup_word) in no_examples:
                            print(lookup_word)
                            defs = get_definitions_new(lookup_word)
                            if defs == 0:
                                print(lookup_word)
                                found = 1
                                break
                            ref = get_reference(line)
                            if ref == '':
                                break
                            output.append({})
                            output[i]['title'] = lookup_word
                            output[i]['left'] = line.find('left').text
                            output[i]['right'] = line.find('right').text
                            output[i]['example'] = wikitext_one_sentence(sentence, orphaned[3:-3])
                            output[i]['left_extra'] = wikilink(sentence[3])
                            output[i]['source'] = get_reference(line)
                            output[i]['verificator'] = 'None'
                            output[i]['correct_num'] = 'None'
                            output[i]['good_example'] = False
                            output[i]['bad_example'] = False
                            output[i]['definitions'] = defs
                            output[i]['orphan'] = orphaned[3:-3]
                            
                            print(wikitext_one_sentence(sentence, orphaned[3:-3]))

                            i+=1
                            found = 1
                            break
                    if found:
                        break

if __name__ == '__main__':
    orphaned_examples()


