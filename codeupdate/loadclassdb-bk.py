#Python
# -*- coding: utf-8 -*-
# Load db with changed sections (from Classification Tables) 
# 
from django.db import models
from codeupdate.models import *
from laws.models import *
from lxml import etree
from cStringIO import StringIO

# To parse the Public Law XML and select a specific section, subsection, para or subpara:
def getxmltree(congress, plnum):
    xfile = PubLaw.objects.get(congress=congress, plnum=plnum).text
    xfile = StringIO(xfile)
    tree = etree.parse(xfile)
    return tree

# XPATH functions
findsec = [
            etree.XPath('//section/enum'), 
            etree.XPath('//subsection/enum'), 
            etree.XPath('//paragraph/enum'), 
            etree.XPath('//subparagraph/enum')
        ]

classlistfile = '/Users/tabulaw/Documents/workspace/uslaw/codeupdate/data/Classtables'

# Split the Classification table up, with these columns:
# [Title, Section, Public Law, PL-section, 125 Stat., details]
def getclasslist(classlistfile):
    with open(classlistfile, 'r') as classtable:
        classlist = [each_line.strip().split(None, 5) for each_line in classtable]
    return classlist

# Parse the PL from the classification table into a list of lists:
# Result is a list of lists, e.g. [[3.,(a),(2),(B)],[(C)]]
def parse_section_number(sections):
    # Splits comma-separated section numbers and removes spaces and quotation marks 
    result = [section.strip('"').strip() for section in sections.split(',')]
    # Separates each part of the section number, e.g. "3(a)(2)(B)" --> "[3.,(a),(2),(B)]"
    base_section = [section for section in result[0].split('(')]
    base_section[0] += '.'
    if len(base_section) > 1:
        base_section[1:] = [('('+section) for section in base_section[1:]]
    result[0] = base_section
    return result

#  else if len(each_line[3].split('-')):
#
#    else:
#        pass

# Find the lowest level for a given section reference: section, subsection, paragraph or subparagraph
def findelements(sections, tree, level):
    # Get element corresponding to the section number, sections[0]
    for element in findsec[level](tree):
        if element.text == sections[0]:
            sections = sections[1:]
            level += 1
            result = [sections, element.getparent(), level]
            return result 
        else:
            pass            
    
# Deal with a range, e.g. "3(a)-4(b)"

def main():
        classlist = getclasslist(classlistfile)
    # for each_line in classlist:
        each_line = classlist[0]

        # Get the XML for the corresponding public law
        congress, plnum = each_line[2].split('-')
        tree = getxmltree(congress, plnum)

        # Grab the PL Section number and parse into a list
        sections = parse_section_number(each_line[3])
        sections = sections[0]        
        level = 0
        #print sections
        # Get the element at the lowest level for the first section listed, e.g. "3(A)(2)(B),(C)" --> paragraph (B)
        while len(sections) > 1:
            print len(sections)
            [sections, tree, level] = findelements(sections, tree, level)
        print [sections, tree, level]
        # Save Elements in the Classification table of codeupdate.models
