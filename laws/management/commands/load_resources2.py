# -*- coding: utf-8 -*-
# Parser for loading data from http://www.gpo.gov/fdsys/bulkdata/CFR/2010/title-26
# We have 2 sources for regulations. This is first one from XML.
# 

from __future__ import with_statement
try:
    import re2 as re
except:
    import re
import os
import shutil
import lxml
import sys
from lxml import etree

from django.core.management.base import BaseCommand

from laws.models import Section, Subsection, Regulation, Title


class Command(BaseCommand):
    help = """Parser for loading data from http://www.gpo.gov/fdsys/bulkdata/CFR/2010/title-26"""

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
                            #print s
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
                            #print s_id
                            subsection = None
                            try:
                                section = Section.objects.get(section=s_id[1], title=title)                            
                            except Section.DoesNotExist:
                                print "Section not found: %s" %s_id[1]
                                section = None
                            else:
                                #print section.id

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
                                    if "PRTPAGE" in t:
                                        s = s.replace('<'+t+'>', " ")
                                    else:
                                        if t == "/E":
                                            s = s.replace('<'+t+'>', " ")
                                        elif t == "/FR":
                                            s = s.replace('<'+t+'>', "</span>")
                                        else:
                                            s = s.replace('<'+t+'>', "</div>")
                                else:
                                    tnew = t.split(" ")[0]
                                    if tnew == "E":
                                        s = s.replace('<'+t+'>', " ")
                                    elif tnew == "FR":
                                        s = s.replace('<'+t+'>', "<span class='"+tnew+"'>")
                                    else:
                                        s = s.replace('<'+t+'>', "<div class='"+tnew+"'>")

                            #print path
                            #print "[%s] => [%s]" %(sectno, sectno.replace("§", "").replace(" ",""))
                            text = s.decode('utf-8')#.encode("utf-8").decode('utf-8')

                            try:
                                res = Regulation.objects.get(section=sectno.replace("§", "").replace(" ",""))
                            except Regulation.DoesNotExist:
                                
                                res = Regulation(section=sectno.replace("§", "").replace(" ",""), title=subject, text=text)
                                res.save()
                            else:
                                res.text = res.text + text
                                res.save()
                            if section:
                                res.sections.add(section)

                            res.id=None

                        #print s
                                   
                    #sys.exit()
        print "Total sections loaded: %s"%i
                    
                
