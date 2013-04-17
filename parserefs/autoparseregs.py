#!/usr/bin/python<2.7>
# -*- coding: utf-8 -*-

import string, os
try:
    import re2 as re
except:
    import re
from splithtml import *
import codecs


# SETTINGS
#regfile = os.path.join(os.path.abspath(os.path.dirname(__file__)),'regulations-regex.txt')
regfile = './regulations-regex.txt'
_DEBUG = False


def makergxlist(regfile):
    rfile = codecs.open(regfile, 'r', 'utf-8')
    findreplace = []
    for eachline in rfile.readlines():
        if (not eachline.isspace()) & (eachline[0] <> '#'):
            pattern_replace = unicode(eachline).strip().split('#')
            findreplace.append(pattern_replace)
    rfile.close()
    findreplace = [(re.compile(pattern, re.U|re.M), replacement) for pattern, replacement in findreplace]
    return findreplace

def subfile(inputfile, findreplace):
    outtext = inputfile
    if inputfile is None:
        return outtext

    for counter, pattern_replace in enumerate(findreplace):
        try:
            outtext, subs = re.subn(pattern_replace[0], pattern_replace[1], outtext)
            if _DEBUG and subs > 0:
                print pattern_replace[0].pattern
                print pattern_replace[1]
                print "=" * 30
        except KeyboardInterrupt:
            print counter, ' substituted: ', subs 
            print pattern_replace[0], "||||", pattern_replace[1], outtext
    return outtext 

def parse(data=False):
    inputfile = [data, ]
    with open(inputfile[0], 'rb') as filename:
        inputtxt = filename.read()
        inputtxt = unicode(inputtxt, errors="ignore")

    # Make initial substitutions
    findreplace = makergxlist(regfile)
    parsedfile = subfile(inputtxt, findreplace)
    #TODO: Find multiple section references
    #TODO: Replace – with - in url , e.g. '1.1001–1(a)' 

    # Clean up
    parsedfile = parsedfile.replace('@','')
    return parsedfile

