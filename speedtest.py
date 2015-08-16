# -*- coding: utf-8 -*-

from klasa import *
import time

t = time.time()

list = getListFromXML('20141024')

i = 1
for elem in list:
    i+=1
    try: h = Haslo(elem)
    except sectionsNotFound:
        pass
    else:
        if h.type == 3:
            tx = parseText(h.content)
            a = tx.index("{{znaczenia}}")
            b = tx.index("{{etymologia}}")
            print(a)
            print('hello')
            print(tx.nodes[a:b])
            h.langs()
            #for template in tx.filter_text():
            #    print u'%s' % template
    if i>1:
        break


elapsed = time.time() - t
print(elapsed)
