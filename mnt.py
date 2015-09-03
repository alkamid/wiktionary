# -*- encoding: utf-8 -*-

from statystyka import *

def meaningsUpdateWikitext(lang, count, text):

    regex = re.compile(r'({\s*?\'%s\'\s*,\s*{[\w\s,=\']*?)(z\s*=\s*[0-9]*)([\w\s,=\']*?})' % lang, re.UNICODE)
    s = re.search(regex, text)
    if s and s.group(2):
        print('hohoho')
        text = re.sub(regex, r'\1z = %d\3' % count, text)
    else:
        regex = re.compile(r'({\s*?\'%s\')\s*(,\s*{)*' % lang, re.UNICODE)
        s = re.search(regex, text)
        if s:
            if s.group(2):
                text = re.sub(regex, r'\1\2 z = %d,' % count, text)
            else:
                text = re.sub(regex, r'\1, { z = %d } ' % count, text)
    return text

inp = codecs.open("ymtext.txt", encoding="utf-8")

text = inp.read()

print(meaningsUpdateWikitext('użycie międzynarodowa', 100, text))
