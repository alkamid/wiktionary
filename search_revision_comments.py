# -*- coding: utf-8 -*-
"""A quick and dirty script to search for revisions with particular
keywords in comments. I used it to determine how many reverts we had
on pl.wikt in 2015"""

from pywikibot import xmlreader
import dateutil.parser as dparser
from datetime import datetime, timezone

pages = xmlreader.XmlDump.parse(xmlreader.XmlDump('plwiktionary-20151226-stub-meta-history.xml.gz', allrevisions=True))

i = 0

start = datetime(2015, 1, 1, tzinfo=timezone.utc)
stop = datetime(2016, 1, 1, tzinfo=timezone.utc)

for a in pages:
    if dparser.parse(a.timestamp) > start and dparser.parse(a.timestamp) < stop and a.comment and any(word in a.comment for word in ['nulowanie', 'ycofano']):
        print(a.comment)
        i += 1

print(i)
