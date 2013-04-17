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
    help = """Import the US legal code from Cornel's XML format."""
    
    
    def handle(self, *args, **options):
        if not len(args) > 0:
            print "Please supply the directory of extracted XML files as the first argument."
            return

        dirname = args[0]
        self.ordering = 0


        xslt_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 '..', '..', 'section.xslt'))
        #print xslt_path
        with open(xslt_path) as f:
            self.xslt = lxml.etree.XSLT(lxml.etree.fromstring(f.read()))

        #self.import_xml("var/xml/uscode26/T01F00026.XML")
        #return

        count = 0
        failed = open('var/failed.txt', 'w')
        for root, dirs, files in os.walk(dirname):
            for filename in files:
                if not filename.lower().endswith(".xml") or 'TOC' in filename:
                    continue
                path = os.path.join(root, filename)
                count += 1
                #print path, "%.02f" % (count / 600.)
                try:
                    self.import_xml(path)
                except Exception, ex:
                    print format_exc()
                    failed.write('FILE: %s\n' % path)
                    failed.write(format_exc() + '\n\n')
                    #sys.exit()
                    

    def found_title(self, filename):
        """
     
        """
        name_re = re.compile(r'<name>(.*?)</name>')
        title_re = re.compile(r'TITLE (\d+)')
        hdsupnest_re = re.compile(r'<hdsupnest(.*?)>(.*?)</hdsupnest>')

        with open(filename) as f:
            for l in f.readlines():
                if "<hdsupnest" in l: # looking for level
                    supnest = hdsupnest_re.findall(l)
                    supnest_text = supnest[0][1]
                    title = title_re.findall(supnest_text)
                    if len(title)>0:
                        if "APPENDIX" in l: # APPENDIX
                            last, c  = Title.objects.get_or_create(title=title[0]+'A', name=supnest_text, parent = None)
                        else:
                            last, c  = Title.objects.get_or_create(title=title[0], name=supnest_text, parent = None)

                    else:
                        try:
                            last, c  = Title.objects.get_or_create(name=supnest_text, parent = last)
                        except:
                            print "Not found: %s "%(supnest_text)
                            print l
                            print filename
        try:
            print last
        except:
            print "Not found:" , filename
            last = False
            #sys.exit()
        self.title_object = last
        return last
    
    def import_xml(self, filename):
        parser = lxml.etree.XMLParser(dtd_validation=False, load_dtd=False,
                                      resolve_entities=False, encoding="utf8")
        with open(filename) as f:
            print "Processing: %s" %filename
            source = os.path.basename(filename)
            file_contents = unescape(f.read())
            file_contents = re.sub('''^<\?xml version="1.0" encoding="UTF-8"\s*\??>''', 
                    '', file_contents)
            file_contents = file_contents.replace("&", "&amp;")
            #try:
            xml = lxml.etree.fromstring(file_contents, parser=parser)                
            #except:
            #    print "----------------------------"
            #    print "Error while parsing XML"
            #    print "file %s"%filename
            #    print sys.exc_info()[0]
            #    return False


            try:
                self.title = xml.attrib['titlenum'].lstrip('0')
                #print "TITLE:, ", self.title
            except KeyError:
                return

            #try:
            #    title_section = xml.xpath('//hdsupnest')[0].text
            #    match = re.match("TITLE (?P<title>\w+)\s*(?:-|&mdash;)\s*(?P<name>\w+)", 
            #            title_section)
            #    if match:
            #        title = match.group('title').lstrip('0')
            #        print "SOME TITLE???!!!!!!", title
 #           for l in file_contents:
            title_object = self.found_title(filename)
            if not title_object:
                return False

            #title_object, c = Title.objects.get_or_create(title=self.title.upper())
            #title_object = Title.objects.get(title=self.title)
            #        self.ordering += 1
            #except IndexError:
            #    pass

            #if title_object.title=='26':
                #print filename
                #import sys
                #sys.exit()
            sections = xml.xpath('//section')
            if len(sections) == 0:
                return
            self.section = sections[0].attrib['num']

            section, c  = Section.objects.get_or_create(title=title_object, section=self.section)
            self.section = section
            body = self.xslt(xml).xpath('//xhtml:body/xhtml:div',
                                        namespaces={
                    'xhtml': 'http://www.w3.org/1999/xhtml'})[0]
            subsection = Subsection(section=section, level=0, text = unicode(lxml.etree.tostring(body)).strip(), source = source, part_id=0)
            #print body
            #print "----\r\n\r\n"
            #print lxml.etree.tostring(body)
            subsection.save_xml()
            self.part_id=0

            section_head = xml.xpath('//section/head')
            for t in section_head:
                head_text =  t.xpath('string()').strip()
                if head_text != '':
                    section.header =  head_text
                    section.save()

            for sect_text in xml.xpath('//section/sectioncontent/text'):
                self.part_id =self.part_id+1
                #self.ordering += 1
                #print 'ORIGIN', lxml.etree.tostring(sect_text)
                #print 'MODIFIED', sect_text.xpath('string()')
                l2 = Subsection(
                    #title=title_object,
                    section=section,
                    part_id=self.part_id,
                    text=unicode(sect_text.xpath('string()')),
                    source=source,
                    level=0)
                #print lxml.etree.tostring((sect_text.xpath('string()')))
                #print "----\r\n\r\n"
                #l2.save()
            self.part_id=0
            for psection in xml.xpath('//section/sectioncontent/psection'):
                self.part_id+=1
                self.parse_psection(psection, [], source)

    def parse_psection(self, psection, parts, source):
        parts.append(psection.xpath('string(enum)'))
        psection_id = psection.attrib['id']

        # Get references
        ref_sections = []
        ref_subsections = []
        ref_titles=[]
        for ref in psection.xpath('text/aref'):
            for subref in ref.xpath('subref'):
                if subref.attrib['type'] == 'title':
                    match = re.match( r"usc_sup_01_([^_])", 
                            subref.attrib['target'])
                    if match:
                        (title,) = match.groups()
                        title = title.lstrip('0')
                        section = ""
                        ref_psec_id = ""
                    else:
                        continue

                elif subref.attrib['type'] in ['sec', 'psec']:
                    match = re.match(
                        r"usc_sec_(?P<title>\d+)_(?P<section>[^-]+)-*(?P<section2>[0-9A-Za-z]*)-?(?:\#(?P<psection>\w+))?",
                        subref.attrib['target'])
                    if not match:
                        continue
                    (title, sec1, sec2, ref_psec_id) = match.groups()
                    title = title.lstrip('0')
                    section = sec1.lstrip('0') + sec2.rstrip('0')
                    ref_psec_id = ref_psec_id or ""

                else:
                    continue
                #print "Title", self.title, "Section:", self.section, "psec_id:", ref_psec_id
                #title_object = self.title_object #found_title(se  = Title.objects.get_or_create(title=title.upper())
                #title_object = Title.objects.get(title=title)
                #if section=='':
                #    ref_titles.append(title_object)
                #else:
                #    s_object, c = Section.objects.get_or_create(title=title_object, section=section)
                #    if ref_psec_id!="":
                #        subs_object,c  = Subsection.objects.get_or_create(section=s_object, subsection=ref_psec_id)#, part_id=self.part_id)
                #        ref_subsections.append(subs_object)
                        #print "SUBS", subs_object
                #    else:
                #        ref_sections.append(s_object)
                        #print "S_OBJECT", s_object
                    
                #if len(matches) == 0:
                #    ref_law = Law.objects.create(
                #            title=title,
                #            section=section,
                #            psection=ref_psec_id,
                #            order=0)
                #else:
                #    ref_law = matches[0]
                #ref_laws.append(ref_law)
        part_id = 0             
        for sub_element in psection:
            self.part_id=self.part_id+1
            if sub_element.tag in ["text", "head"]:
                #self.ordering += 1
                title_object = self.title_object #Title.objects.get_or_create(title=self.title.upper())
                #title_object = Title.objects.get(title=self.title)
                section_object = self.section #, c = Section.objects.get_or_create(title=title_object, section=self.section)
                try:
                    #print section_object, psection_id
                    subsection, c = Subsection.objects.get_or_create(section=section_object, subsection=psection_id)#, part_id=self.part_id)
                except Subsection.MultipleObjectsReturned:
                    subsection = Subsection.objects.filter(section=section_object, subsection=psection_id).order_by('part_id')[0]#, part_id=self.part_id)

                #matches = Law.objects.filter(
                #        title=self.title,
                #        section=self.section,
                #        psection=psection_id)
                #if len(matches) == 1 and not matches[0].source:
                #    law = matches[0]
                #else:
                #    law = Law(
                #        title=self.title,
                #        section=self.section,
                #        psection=psection_id)
                subsection.level = int(psection.attrib['lev'])
                subsection.text = unicode(sub_element.xpath('string()') or "")
                #law.order = self.ordering
                subsection.source = source
                #law.set_name(parts)
                subsection.save()
            elif sub_element.tag == "psection":
                self.parse_psection(sub_element, parts, source)
        
        title_object = self.title_object #,c = Title.objects.get_or_create(title=self.title.upper())
        #title_object = Title.objects.get(title=self.title)
        section_object = self.section #Section.objects.get(title=title_object, section=self.section)
        #print "Attaching to", section_object.section, section_object.id

        #print "================================================"
        #if ref_sections:
            #section = Section.objects.filter(title=title_object, section=self.section, 
            #        psection=psection_id)[0]
        #    for r in ref_sections:
        #        section_object.reference_section.add(r)
                #print ref_sections
        #        section_object.save()
        #if ref_subsections:
            #section = Section.objects.filter(title=title_object, section=self.section, 
            #        psection=psection_id)[0]
        #    for r in ref_subsections:
        #        section_object.reference_subsection.add(r)
        #        section_object.save()
        #if ref_titles:
            #section = Section.objects.filter(title=title_object, section=self.section, 
            #        psection=psection_id)[0]
        #    for r in ref_titles:
        #        section_object.reference_title.add(r)
        #        section_object.save()

        parts.pop()
