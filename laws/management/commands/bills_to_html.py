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

from laws.models import *

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
    help = """Import the US legal code from Cornel's XML format."""
    
    
    def handle(self, *args, **options):

        xslt_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 '..', '..', 'billres.xsl'))
        #print xslt_path
        with open(xslt_path) as f:
            self.xslt = lxml.etree.XSLT(lxml.etree.fromstring(f.read()))

        #self.import_xml("var/xml/uscode26/T01F00026.XML")
        #return

        count = 0
        failed = open('var/failed.txt', 'w')
        for b in PubLaw.objects.all():
#        with open("laws/bill_xml.xml") as b:
            #print b.text
            #sys.exit()
            print "Processing", b.id
            try:
                self.import_xml(b)
            except Exception, ex:
                print format_exc()
                
    
    def import_xml(self, publaw):
        parser = lxml.etree.XMLParser(dtd_validation=False, load_dtd=False,
                                      resolve_entities=False, encoding="utf8")
        file_contents = publaw.text
        file_contents = re.sub('''^<\?xml version="1.0" encoding="UTF-8"\s*\??>''', 
                    '', file_contents)
        file_contents = file_contents.replace("&", "&amp;")
            #try:
        xml = lxml.etree.fromstring(file_contents, parser=parser)
        section_start, subsection_start = False, False
        paragraph_start = False
        for cl in Classification.objects.filter(pl=publaw):
            sections = cl.plsection.split(",")
            #print sections
            section_list = []
            j = 0
            for s in sections:
                if j>0:
                    if s.strip().startswith("("): #this subsection, second
                        section = section_list[0]["section"]
                        subsection = s.strip()
                    else:
                        section = s.strip()
                        subsection = ""
                else:
                    if s.strip().startswith("("):
                        section = ""
                        subsection = s.strip()
                    if "(" in s:
                        section = s[:s.find("(")]
                        subsection = s[s.find("("):]
                    else:
                        section = s.strip()
                        subsection = ""

                    section_list.append({"section":section, "subsection":subsection,})                        
                j += 1

            for element in xml.iter():
    #            print("%s - %s" % (element.tag, element.text))
                if element.tag == "section":  #
                    section_start = True
                    print "Section:"
                    current_subsection = ""
                    section_id = element.get("id")
                if section_start and element.tag=="enum":
                    try:
                        current_section = element.text.replace(".","")
                    except:
                        current_section = False
                    else:
                        print current_section
                        if subsection == "" and section == element.text.replace(".",""):
                            cl.sectionid = section_id
                            cl.save()

                if element.tag == "subsection":
                    subsection_start = True
                    section_start = False
                    subsection_id = element.get("id")
                  
                if subsection_start and element.tag=="enum":
                    #print "Subsection", element.text
                    try:
                        current_subsection = element.text
                    except:
                        current_subsection = ""
                    else:
                        if subsection!="":
                            if section == current_section and subsection == current_subsection:
                                cl.sectionid = subsection_id
                                cl.save()
                            
                            
                if element.tag == "paragraph":
                    paragraph_start = True
                    section_start = False
                    subsection_start = False
                    paragraph_id = element.get("id")
                  
                if paragraph_start and element.tag=="enum":
                    #print "Paragraph", element.text
                    try:
                        current_subsection += element.text
                    except:
                        pass
                    else:
                        if subsection!="":
                            if section == current_section and subsection == current_subsection:
                                cl.sectionid = paragraph_id
                                cl.save()

                if element.tag !="section" and element.tag!="subsection" and element.tag!="paragraph":
                    section_start, subsection_start = False, False
                    paragraph_start = False

#        for e in xml:
#            if e.tag=="legis-body":
#                for t in e:
#                    if t.tag == "section": # loop over sections
#                        for elem in t:
#                            if elem.tag == "enum":
#                                print "Section %s"%elem.text.strip(".")
#                                print t.get("id")
#                            if elem.tag=="subsection":
#                                for sub in elem:# loop over subsections
#                                    print "ID", sub.tag, sub.get("id")
                            #print elem.text
        #sys.exit()
        publaw.html = html = unicode(str(self.xslt(xml)).decode("utf-8"))
        if html is None:
            print "Can't convert to html"
            sys.exit()

        publaw.save()
        
