#!/usr/bin/python
# -*- coding: utf-8 -*-

# robienie listy haseł polskich bez wymowy

import sys
sys.path.append('/home/alkamid/wikt/pywikipedia')
#sys.path.append('/home/adam/pywiki/pywikipedia')
import codecs
from pywikibot import Category
import pywikibot
from pywikibot import pagegenerators
import re
import math
import datetime

def main():


    r = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n<html xmlns="http://www.w3.org/1999/xhtml\nxml:lang="pl">\n<head>\n<meta http-equiv="content-type" content="text/html; charset=UTF-8" />\n</head><body>'
    r = r + 'błąźć<br /> ółąś<br />żóć'
    r = r + '</body></head>'
    file = open("/home/alkamid/public_html/wym1.htm", 'w')
    file.write(r.encode( "utf-8" ))
    file.close


if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
