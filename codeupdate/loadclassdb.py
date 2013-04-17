#Python
# -*- coding: utf-8 -*-
# Load db with changed sections (from Classification Tables) 
# 
from django.db import models
from codeupdate.models import *
from laws.models import *
from lxml import etree
from cStringIO import StringIO
import re

# To parse the Public Law XML and select a specific section, subsection, para or subpara:
def getxmltree(congress, plnum):
    xfile = PubLaw.objects.get(congress=congress, plnum=plnum).text
    try:
        xfile = StringIO(xfile)
        tree = etree.parse(xfile)
    except TypeError:
        tree = None
    return tree

# XPATH functions
findsec = [
            etree.XPath('//section/enum'), 
            etree.XPath('//subsection/enum'), 
            etree.XPath('//paragraph/enum'), 
            etree.XPath('//subparagraph/enum')
        ]

classlistfile = '/Users/tabulaw/Documents/workspace/uslaw/codeupdate/data/Classtables112'

# Split the Classification table up, with these columns:
# [Title, Section, Public Law, PL-section, 125 Stat., details]
def getclasslist(classlistfile):
    with open(classlistfile, 'r') as classtable:
        classlist = [each_line.strip().split(None, 5) for each_line in classtable]
    return classlist

# Parse the PL from the classification table into a list of lists:
# Result is a list of lists, e.g. [[3.,(a),(2),(B)],[(C)]]
def parse_section_number(sections):
    # Split comma-separated section numbers
    result = sections.split(',')
    # Separate '(x)' with dashes, then split on the dash 
    result = [re.sub(r'(\(\w\))', r'-\1',section) for section in result]
    result = [section.split('-') for section in result]
    # functions for results that have two sections (start and end)
    try:
        if result[1].strip('"') != result[1]:
            result[1] = result[1].strip('"')
        else:
            # For comma or dash separated values, e.g. "['3','(a)'],['','(b)']" --> "['3','(a)'],['(b)']"
            result[1] = result[1][1:]
    except:
            pass
    return result

# Find the section number corresponding to the sections and depth 
def findelements(sections, tree, depth, capture):
    # Get element corresponding to the section number, sections[0]
    priorelements = []
    for element in findsec[depth](tree):
        if element.text == sections[0]:
            sections = sections[1:]
            depth += 1
            result = [sections, element.getparent(), depth]
            #result = [sections, priorelements + [element.getparent()], depth]
            return result 
        else:
            if capture:
                priorelements += [element.getparent()]
    
# Deal with a range, e.g. "3(a)-4(b)"

def main():
     classlist = getclasslist(classlistfile)
     for each_line in classlist:
        #each_line = classlist[0]

        # Get the XML for the corresponding public law
        congress, plnum = each_line[2].split('-')
        plnum = plnum.zfill(3)
        tree = getxmltree(congress, plnum)
        try:
            # Grab the PL Section number and parse into a list
            plsection = each_line[3]
            sections = parse_section_number(plsection)
            if len(sections) == 1:
                sections = [sections]
            depth = 0
            section = sections[0]
            capture = False

            # Get the element at the lowest depth for the first section listed, e.g. "3(A)(2)(B),(C)" --> paragraph (B)
            while len(section) > 1:
                [section, tree, depth] = findelements(section, tree, depth, capture)
            plsectiontext = etree.tostring(tree, encoding=unicode, method='text')

            #Select all nodes below the parent of the section that was found
            #tree = tree.getnext()
            capture = True
            # Save Elements in the Classification table of codeupdate.models
            try:
                classelement = Classification(
                                                pl= PubLaw.objects.get(congress=congress, plnum=plnum),
                                                plsection = plsection,
                                                plsectiontext = etree.tostring(tree),
                                               #TODO:Assign corresponding USC sections
                                               # uscsection = title='26', section=each_line[1],
                                               # uscsubsection - Currently none in the Classification tables;
                                            )
                classelement.save()
                print 'saved '+str(classelement.pl) +" "+ str(classelement.plsection)
            except:
                print "Couldn't save " + plsection + " to Classification table"

        except:
            print "Error on section: "+str(section)
            pass
