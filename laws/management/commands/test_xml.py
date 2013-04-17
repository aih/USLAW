# -*- coding: utf-8 -*-
from __future__ import with_statement
try:
    import re2 as re
except:
    import re
import os
import sys
import lxml.etree
from traceback import format_exc

from django.core.management.base import BaseCommand
from django.utils.encoding import force_unicode
from django.conf import settings

from laws.models import Title, Section, Subsection

import htmlentitydefs


# Do not save millions of quries into connection.quries
settings.DEBUG = False

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

class Command(BaseCommand):
    help = """Import the US legal code TOC"""

    def handle(self, *args, **options):
        if not len(args) > 0:
            print "Please supply the directory of extracted XML files as the first argument."
            return

        dirname = args[0]
        self.ordering = 0
        count = 0

        for root, dirs, files in os.walk(dirname):
            for filename in files:
                if not filename.lower().endswith(".xml") and not 'TOC' in filename:
                    continue
                path = os.path.join(root, filename)
                count += 1
                #print path, "%.02f" % (count / 600.)
                #try:
                self.import_toc(path)
                #except Exception, ex:
                #    print format_exc()
                    #failed.write('FILE: %s\n' % path)
                    #failed.write(format_exc() + '\n\n')
                    


    def import_toc(self, filename):
        print "Processing %s"%filename
        name_re = re.compile(r'<name>(.*?)</name>')
        title_re = re.compile(r'TITLE (\d+)')
        hdsupnest_re = re.compile(r'<hdsupnest(.*?)>(.*?)</hdsupnest>')
        sec_re = re.compile(r'<sec refid=(.*?)>(.*?)\.(.*?)</sec>')
        sec2_re = re.compile(r'<sec refid=(.*?)>(.*?) (.*?)</sec>')

        title_found = False
        supnest_found = False
        last = False
        tree = []
        r = 0
        with open(filename) as f:
            for l in f.readlines():
                if "<hdnestgrp>" in l: # title/name
                    r+=1
                if r>1:
                    print "%s have %s gr" %(filename, r)
                    sys.exit()
