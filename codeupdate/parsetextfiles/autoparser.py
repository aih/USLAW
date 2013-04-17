# Python

import os, sys, re, subprocess
from subprocess import PIPE, Popen
from MakeRList import makeRList
from subdir import subfile

# The process below is to parse files that are not available in XML format
# To parse the Public Law XML and select a specific subsection:
# from lxml import etree
# xfile = open('./path/to/file')
# tree = etree.parse(xfile)
# r = tree.xpath('legis-body/section[2]/subsection')
# 

location = "/Users/tabulaw/Documents/workspace/uslaw/codeupdate/newlaws/"
regfile = './regexfns.txt'

def main():
    # Compiles regex substitutions
    rlist = makeRList(regfile)
    findreplace = [(re.compile(pattrn,re.U|re.M), replacement) for pattrn, replacement in rlist]
    
    # Apply to filenames in the directory at 'location'
    for fname in os.listdir(location):
        fullpath = location+"/"+fname
        with open(fullpath,'r') as lawfile:

            #Skip the table of Contents

            for each_line in lawfile:

            #iterate sections of the form Title; Subtitle; Sec. or SEC. or SECTION; (a)(1)(A)(i)
            # Finds the first section heading
                s = re.search(r'--\(1\)',each_line.lstrip()).group()
                if s:
                    sections_list.append(s)

                s= re.search(r'^\([0-9A-Za-z]\)',each_line.lstrip()).group()
                if s:
                    sections_list.append(s)

            # Print the accumulated sections at the beginning of the line until finding the next section heading
            print sections_list
            # Parses the output, with the Regex patterns in findreplace and writes the parsed data to a file
            #parsedfile = subfile(parsedfile, findreplace)
