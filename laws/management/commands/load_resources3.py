# -*- coding: utf-8 -*-
from __future__ import with_statement
try:
    import re2 as re
except:
    import re
import os
import shutil
from lxml import etree
import lxml
import sys

from django.core.management.base import BaseCommand

from laws.models import Section, Subsection, Resource, Title

class Command(BaseCommand):
    help = """Import the US legal code from Cornel's XML format."""

    def handle(self, *args, **options):
        if len(args) == 0:
            print "Please supply the directory of source XML files as the first argument."
            return

        dirname = args[0]
        i=0
        f = open("regulations.xslt")
        xslt = lxml.etree.XSLT(lxml.etree.fromstring(f.read()))
        f.close()
        d={}
        title = Title.objects.get(title='26')
        for root, dirs, files in os.walk(dirname):
            for filename in files:
                path = os.path.join(root, filename)
                print "Processing", path
                
                with open(path) as f:
                    parser = lxml.etree.XMLParser(dtd_validation=False, load_dtd=False,
                                      resolve_entities=False, encoding="utf8")
                    data = f.read()
                    sectid_re = re.compile(r'<SECTNO>§ (\w+)\.(\d+)(.*?)([-\w]*)</SECTNO>')
                    sectno_full_re = re.compile(r'<SECTNO>(.*?)</SECTNO>')
                    subject_re = re.compile(r'<SUBJECT>(.*?)</SUBJECT>')
                    sect = re.compile(r'<SECTION>(.*?)</SECTION>', re.DOTALL)
                    sections = sect.findall(data)

                    tag_re = re.compile(r'<(.*?)>')
                    for s in sections:
                        sect_id = sectid_re.findall(s)

                        try:
                            subject = subject_re.findall(s)[0]
                        except:
                            print s
                            subject = ""
                        sectno = sectno_full_re.findall(s)[0]
                        print subject
                        if len (sect_id)==0:
                            print s
                        #print "Section id:", sect_id[0]
                        try:
                            s_id = sect_id[0]
                        except:
                            s_id=False

                        if s_id and s_id[0]=='1':
                            print s_id
                            subsection = None
                            try:
                                section = Section.objects.get(section=s_id[1], title=title)                            
                            except Section.DoesNotExist:
                                print "Section not found: %s" %s_id[1]
                                section = None
                            else:
                                print section.id

                                try:
                                    subsection = Subsection.objects.get(section=section, subsection=s_id[2])                            
                                except Subsection.DoesNotExist:
                                    #print "SubSection not found: %s" %s_id[1]
                                    subsection = None
                                else:
                                    print section.id


                            section_re = re.compile(r'')
                            tags = tag_re.findall(s)
                            for t in tags:
                                if "/" in t:
                                    s=s.replace('<'+t+'>', "</div>")
                                else:
                                    tnew =t.split(" ")[0]
                                    s=s.replace('<'+t+'>', "<div class='"+tnew+"'>")


                            res = Resource(title=sectno+' '+subject, section=sectno.replace(" ", ""), text=s, source_type=0)
                            print res.section, sectno
                            res.save()
                            if section:
                                res.sections.add(section)

                            res.id=None

                        #print s
                                   
                    #sys.exit()
        print "Total sections loaded: %s"%i
                    
                
