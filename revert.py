#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append('/home/alkamid/wikt/pywikipedia')
#sys.path.append('/home/adam/pywiki/pywikipedia')
import pywikibot. query, userlib

__version__ = '$Id: revertbot.py 7957 2010-02-24 14:26:58Z xqt $'

"""
    (c) Bryan Tong Minh, 2008
    (c) Pypywikibot.team, 2008-2010
    Licensed under the terms of the MIT license.
"""

class BaseRevertBot(object):
    """ Base revert bot

    Subclass this bot and override callback to get it to do something useful.
    """
    def __init__(self, site, comment = None):
        self.site = site
        self.comment = comment

    def get_contributions(self, max = 24, ns = None):
        predata = {
            'action': 'query',
            'list': 'usercontribs',
            'uclimit': '24',
            'ucuser': self.site.username(),
        }
        if ns: predata['ucnamespace'] = ns
        if max < 500 and max != -1: predata['uclimit'] = str(max)

        count = 0
        iterator = iter(range(0))
        never_continue = False
        while count != max or never_continue:
            try:
                item = next(iterator)
            except StopIteration:
                self.log('Fetching new batch of contributions')
                data = query.GetData(predata, self.site)
                if 'error' in data:
                    raise RuntimeError(data['error'])
                if 'query-continue' in data:
                    predata['uccontinue'] = data['query-continue']['usercontribs']
                else:
                    never_continue = True
                iterator = iter(data['query']['usercontribs'])
            else:
                count += 1
                yield item

    def revert_contribs(self, callback = None):
        self.site.forceLogin()

        if callback is None:
            callback = self.callback

        contribs = self.get_contributions()
        for item in contribs:
            try:
                if 1 and item['title'] != 'Wikipedysta:AlkamidBot/wymowa' and item['title'] != 'Wikipedysta:AlkamidBot/zch/log' and item['title'] != 'Wikipedysta:AlkamidBot/wymowa/gwary' and item['title'] != 'Wikipedysta:Alkamid/statystyka/multimedia' and item['title'] != 'Wikipedysta:Alkamid/statystyka/długość średnia' and item['title'] != 'Wikipedysta:Alkamid/statystyka/długość' and item['title'] != 'Wikisłownik:Dlaczego_Wikisłownik':
                    result = self.revert(item)
                    if result:
                        self.log('%s: %s' % (item['title'], result))
                    else:
                        self.log('Skipped %s' % item['title'])
                else:
                    self.log('Skipped %s by callback' % item['title'])
            except StopIteration:
                return

    def callback(self, item):
        #return 'top' in item
        return 1

    def revert(self, item):
        predata = {
            'action': 'query',
            'titles': item['title'],
            'prop': 'revisions',
            'rvprop': 'ids|timestamp|user|content',
            'rvlimit': '2',
            'rvstart': item['timestamp'],
        }
        data = query.GetData(predata, self.site)

        if 'error' in data:
            raise RuntimeError(data['error'])

        pages = data['query'].get('pages', ())
        if not pages: return False
        page = next(iter(pages.values()))
        if len(page.get('revisions', ())) != 2: return False
        rev = page['revisions'][1]

        comment = 'Reverted to revision %s by %s on %s' % (rev['revid'],
            rev['user'], rev['timestamp'])
        if self.comment: comment += ': ' + self.comment

        page = pywikibot.Page(self.site, item['title'])
        pywikibot.output("\n\n>>> \03{lightpurple}%s\03{default} <<<" % page.aslink(True, True))
        old = page.get()
        new = rev['*']
        pywikibot.showDiff(old, new)
        page.put(new, comment)
        return comment

    def log(self, msg):
        pywikibot.output(msg)

import re

class myRevertBot(BaseRevertBot):

    def callback(self, item):
        if 'top' in item:
            page = pywikibot.Page(self.site, item['title'])
            text=page.get()
            pattern = re.compile('\[\[.+?:.+?\..+?\]\]', re.UNICODE)
            return pattern.search(text) >= 0
        return False

def main():
    item = None
    for arg in pywikibot.handleArgs():
        continue
    bot = myRevertBot(site = pywikibot.Site())
    bot.revert_contribs()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
