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
import pywikibot as pwb
from datetime import datetime, timedelta, time

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

def get_reference(api_output, hashtable):
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
    
    if len(hashtable) == 0:
        ref = 'Nazwisko Autora'
    else:
        author_hash = bytes(api_output.find('hash').text, 'utf-8')
        try: ref = hashtable[author_hash].decode('utf-8')[4:-5].replace('</au><au>', ', ')
        except KeyError:
            return ''
    
    match = api_output.find('match').text.lower()
    
    excluded_titles = ['Wikipedia:']

    # article title exists for newspaper records
    article_title = api_output.find('title_a')
    if article_title is not None:
        if any(article_title.text.startswith(c) for c in excluded_titles):
            return ''
        elif len(article_title.text) > 0:
            if len(ref):
                ref += ', '
            ref += '\'\'{0}\'\''.format(article_title.text)



    # this is a book title or a newspaper name
    pub_title = api_output.find('title_mono')
    if pub_title is not None:
        if article_title.text.lower().startswith(match) and 'Wikipedia' in pub_title.text:
            return '' # Wikipedia pages about matched words are probably
            # the best examples
        ref += ', '
        if article_title.text == '':
            ref += '\'\''
        ref += pub_title.text.strip()
        if article_title.text == '':
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
        tuple:
            str: all definitions found in page along with their part of speech
            descriptions
            pywikibot.Timestamp: time at which definitions were retrieved (useful
                for checking for edit conflicts
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

                    return (re.sub(re_refs, '', langsection.subSections['znaczenia'].text), pwb.Page(pwb.Site(), word).editTime())

    return 0


class ExampleDict(dict):
   def __init__(self,*arg,**kw):
      super(ExampleDict, self).__init__(*arg, **kw)
      self['examples'] = []


def log_verification(verified_entry, example_index, error=''):

    #format: title##bool(good_example)##verificator##example##correct_def##error

    #https://regex101.com/r/nN1bN2/2

    this_example = verified_entry['examples'][example_index]
    re_correct_def = re.compile(r'(?:\: \(' + re.escape(this_example['correct_num']) + r'\)\s{0,1}(.*?))(?=\n\: \([0-9]\.[0-9]{1,2}\)|\n\'\'|\n\{\{|$)', re.DOTALL)
    
    todays_date = (datetime.today()).strftime('%Y%m%d')

    with open('log/{0}_examples.log'.format(todays_date), 'a') as f:
        log_line = ''
        log_line += verified_entry['title']

        log_line += '##' + ('1' if this_example['good_example'] else '0')

        for field in ['verificator', 'example']:
            log_line += '##' + this_example[field]

        s_correct_def = re.search(re_correct_def, verified_entry['definitions'])
        if s_correct_def:
            log_line += '##' + s_correct_def.group(1)
        elif this_example['bad_example'] == True:
            log_line += '##none'
        else:
            error += ';cant_find_correct_def'

        if error != '':
            log_line += '##' + error
        else:
            log_line += '##' + none

        f.write('\n' + log_line)
        print(log_line)

def add_example_to_page(verified_entry):
        
    fetch_time = datetime.strptime(verified_entry['fetch_time'], '%Y-%m-%dT%H:%M:%SZ') 
    
    try: page = Haslo(verified_entry['title'])
    except sectionsNotFound:
        pass
    except WrongHeader:
        pass
    else:
        if page.type == 3:
            for lang_section in page.listLangs:
                if lang_section.lang == 'polski':

                    changes = False
                    verificators = set()
                    edit_conflict = pwb.Page(pwb.Site(), verified_entry['title']).editTime() > fetch_time

                    good_example_indices = [ex['good_example'] for ex in verified_entry['examples']]
                    if sum(good_example_indices) > 0:
                        lang_section.pola()

                    for ix, verified_example in enumerate(verified_entry['examples']):
                        if verified_example['bad_example'] == True:
                            log_verification(verified_entry, ix)
                        elif verified_example['good_example'] == True:
                            if edit_conflict:
                                log_verification(verified_entry, ix, 'edit_conflict')
                                return -1

                            lang_section.subSections['przykłady'].add_example(verified_example['correct_num'], verified_example['example'] + '<ref>{0}</ref>'.format(verified_example['source']))
                            lang_section.saveChanges()
                            verificators.add(verified_example['verificator'])
                            changes = True

                    if changes:
                        if len(verificators) > 1:
                            comment = ''
                            for i, ver in enumerate(verificators):
                                if i > 0:
                                    comment += ', '
                                comment += '[[User:{0}|{0}]]'.format(ver)
                            comment = 'Weryfikatorzy: ' + comment
                        else:
                            (only_ver, ) = verificators
                            comment = 'Weryfikator: [[User:{0}|{0}]]'.format(only_ver)
                        
                        page.push(offline=True, myComment='[[Wikiprojekt:Dodawanie przykładów]]. Źródło przykładu: nkjp.pl. {0}'.format(comment))
                        for i, ex in enumerate(good_example_indices):
                            if ex:
                                log_verification(verified_entry, i)
                    return 0
    
    log_verification(verified_entry, 'not_written_to_page')

def dewikify(input_text):
    #https://regex101.com/r/yB0pZ6/1
    re_base_form = re.compile(r'(\[\[(?:[^\]\|]*?\||)(.*?)\]\])')
    dewikified = re.sub(re_base_form, r'\2', input_text)
    return dewikified

def sweep_all_pages():
    
    buffer_size = 20
    site = pwb.Site()
    prefix = 'Wikisłownik:Dodawanie_przykładów/dane/'
    
    with open('output/example_queue.json', 'r') as inp:
        example_queue = json.loads(inp.read())
    
    for i in range(100):
        page = pwb.Page(site, prefix + '{0:03d}'.format(i))
        page_remaining_examples = check_verifications(page)
        if page_remaining_examples != -1:
            while(len(page_remaining_examples) < buffer_size):
                page_remaining_examples.append(example_queue.pop())
                if len(example_queue) == 0:
                    return -1

            with open('output/example_queue_test.json', 'w') as out:
                json_output = json.dumps(example_queue, ensure_ascii=False, indent=4)
                out.write(json_output)
                page.text = json_output
                page.save(comment='Pobranie nowych przykładów z NKJP.pl')

def check_verifications(page):

    anon_edit = False

    new_revid = page.latest_revision_id

    for a in page.revisions():
        if not anon_edit and a.anon == True:
            anon_edit = True

        if a.user == 'Alkamid':
            old_revid = a.revid
            break


    if new_revid != old_revid:
        old = json.loads(page.getOldVersion(old_revid))
        new = json.loads(page.text)
    else:
        return -1

    #we can't really get anonymous editors' IP from JS, so this is
    #a way of retrieving them from page history
    if anon_edit:
        for ix, verified_word in enumerate(new):
            for ex_ix, verified_example in enumerate(verified_word['examples']): 
                if verified_example['verificator'] == None:
                    for rev in page.revisions():
                        temp = json.loads(page.getOldVersion(rev.revid))
                        if temp[ix]['examples'][ex_ix]['verificator'] != None:
                            verified_word['examples'][ex_ix]['verificator'] = previous_user
                            break
                        previous_id = rev.revid
                        previous_user = rev.user
                        if rev.revid == old_revid:
                            break

    revised_wordlist = []
    for verified_word in new:
        found = 0
        for verified_example in verified_word['examples']:
            if verified_example['good_example'] == True or verified_example['bad_example'] == True:
                add_example_to_page(verified_word)
                found = 1
                break
        if not found:
            revised_wordlist.append(verified_word)

    return revised_wordlist

import gzip                                                           
                                                                      
def read_author_hashtable():                                          
    mydict = {}                                                       
    with gzip.open('input/authors_under3.tab.gz', 'r') as f:                
        i = 0                                                         
        for line in f:                                                
            mydict[line[:32]] = line[33:-1]                           
            #i+=1                                                      
            #if i > 10:                                                
            #    break                                                 
    return mydict                                                     

def fetch_active_words():
    page_prefix = 'Wikisłownik:Dodawanie_przykładów/dane/'
    
    active_words = []
    inactive_words = []
    for i in range(100):
        page = pwb.Page(pwb.Site(), page_prefix + '{0:03d}'.format(i))
        text = json.loads(page.text)
        for j in text:
            found = 0
            for k in j['examples']:
                if k['good_example'] or k['bad_example']:
                    active_words.append(j['title'])
                    found = 1
                    break
            if not found:
                inactive_words.append(j['title'])
                
    print(active_words)
    return {'active': active_words, 'inactive': inactive_words}


import os
def read_edit_history():

    added = []
    bad_examples = []
    for file in os.listdir("log"):
        if file.endswith("examples.log"):
            with open('log/' + file, 'r') as inp:
                for line in inp:
                    lsp = line.split('##')
                    if len(lsp) > 3:
                        if lsp[0] == '1':
                            added.append(lsp[1])
                        elif lsp[1] == '0':
                            bad_examples.append(dewikify(lsp[2]))

    return {'added': added, 'bad_examples': bad_examples}


import random
def orphaned_examples(test_word=None, hashtable=None, online=False, complete_overwrite=False):

    buffer_size = 20 #how many words will be printed on one page
    active_words = fetch_active_words() # prepare only as many pages as we need at the moment
    edit_history = read_edit_history()
    excluded_words = active_words['active'] + edit_history['added']

    with open('output/empty_sections.txt', 'r') as g:
        empty_sections = g.readlines()
        random.shuffle(empty_sections)

    if not complete_overwrite:
        excluded_words += active_words['inactive']
    
    if not hashtable:
        authors_hashtable = read_author_hashtable()
    else:
        authors_hashtable = hashtable

    site = pwb.Site()

    # this is a dirty trick, because morfAnalyse() and wikilink() don't
    # really work as they should. The following regex extracts the first part
    # of [[these|links]]
    re_base_form = re.compile(r'\[\[(.*?)(?:\||\]\])')


    words_count = 0
    with open('output/porzucone.txt') as f,\
    open('output/empty_sections.txt', 'r') as g:

        # list of pages with no examples (obtained by empty_section.py)
        orphans = f.read()
        
        # for testing purposes
        if test_word:
            g = [test_word]

        pages_count = 0 #loop helper
        output = [] #list-container for examples

        for input_word in empty_sections:
            
            if complete_overwrite == False and words_count > 2*len(active_words['active']):
                with open('output/example_queue.json', 'w') as o:
                    formatted_output = json.dumps(output, ensure_ascii=False, indent=4)
                    o.write(formatted_output)
                return 2
            
            if pages_count == 100:
                return 0

            # dealing with various list formats, e.g. *[[word]]
            input_word = input_word.strip('*[]\n')
            if len(input_word) < 4 or input_word.upper == input_word:
                continue

            if input_word in excluded_words:
                continue

            print(input_word)

            if complete_overwrite:
            # write to file/page every N words
                if len(output) == buffer_size:
                    if online:
                        formatted_output = json.dumps(output, ensure_ascii=False, indent=4)
                        output_page = pwb.Page(site, 'Wikisłownik:Dodawanie przykładów/dane/{0:03d}'.format(pages_count))
                        output_page.text = formatted_output
                        output_page.save(comment='Pobranie nowych przykładów z NKJP.pl')

                    with open('output/json_examples_{0}.json'.format(pages_count), 'w') as o:
                        o.write(formatted_output)
                        pages_count += 1
                        output = []


            if input_word[0] == '-' or input_word[-1] == '-' or input_word[0].isupper():
                continue # let's skip prefixes and sufixes for now, also whatever starts with a capital leter

            root = etree.parse(nkjp_lookup('{0}**'.format(input_word).replace(' ', '** '))).getroot()

            if root.find('concordance') is not None:
                found = 0
                found_orphan = 0

                defs = get_definitions(input_word)
                if defs == 0:
                    continue

                new_word = ExampleDict()
                new_word['title'] = input_word
                new_word['fetch_time'] = str(defs[1])
                new_word['definitions'] = defs[0]

                for line in root.find('concordance').findall('line'):

                    sentence = extract_one_sentence(line, input_word)

                    if check_sentence_quality(sentence) == 0:
                        continue

                    ref = get_reference(line, authors_hashtable)
                    if ref == '':
                        break

                    if len(new_word['examples']) < 2:
                        temp_example = {'verificator': 'None', 'correct_num': 'None', 'good_example': False, 'bad_example': False}
                        #temp_example['left'] = line.find('left').text
                        #temp_example['right'] = line.find('right').text
                        temp_example['example'] = wikitext_one_sentence(sentence, input_word)
                        temp_example['left_extra'] = wikilink(sentence[3])
                        temp_example['source'] = ref
                        temp_example['orphan'] = None
                        new_word['examples'].append(temp_example)

                    else:
                        # see "dirty trick" note above
                        allwords = re.findall(re_base_form, wikilink(sentence[0] + sentence[2]))
                        for lookup_word in allwords:
                            #for now, reflective verbs are not included in "missing example" list
                            #hence this trick
                            if ' się' in lookup_word:
                                lookup_word = lookup_word[:-4]

                            if '\n*[[{0}]]\n'.format(lookup_word) in orphans:
                                new_example = new_word['examples'][0]
                                new_example['orphan'] = lookup_word
                                #new_example['left'] = line.find('left').text
                                #new_example['right'] = line.find('right').text
                                new_example['example'] = wikitext_one_sentence(sentence, input_word)
                                new_example['left_extra'] = wikilink(sentence[3])
                                new_example['source'] = ref
                                #new_example['definitions'] = defs[0]
                                found_orphan = 1
                                break
                        if found_orphan:
                            break

                if new_word and len(new_word['examples']) > 0:
                    output.append(new_word)
                    words_count += 1


if __name__ == '__main__':
    orphaned_examples()


