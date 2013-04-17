# -*- coding: utf-8 -*-
# Load and parse US Code files from here - http://uscode.house.gov/download/ascii.shtml

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
from django.conf import settings

from laws.models import *
from utils.load_url import load_url
from laws_utils import found_sections
from datetime import datetime

_BASE_URL = "http://uscode.house.gov"
_DOWNLOAD_URL = "http://uscode.house.gov/download/"
_START_URL = "http://uscode.house.gov/download/ascii.shtml"

class Command(BaseCommand):
    help = """Load and parse US Code"""


    def parse_section(self, text):
        return None
    def text_log(self, text):
        f = open("log.txt", "a")
        f.write("%s: %s \r\n"%(datetime.now(), text))
        f.close()

    def parse_chapter(self, data):
        """
        Parse and load chapters from uscode.house.gov/download/
        
        """
        expcite_re = re.compile(r'-EXPCITE-(.*?)-HEAD-', re.DOTALL)
        expcite_re2 = re.compile(r'-EXPCITE-(.*?)-STATUTE-', re.DOTALL)
        expcite_re3 = re.compile(r'-EXPCITE-(.*?)-MISC1-', re.DOTALL)
        title_text_re = re.compile(r'-MISC1-(.*?)-End-', re.DOTALL)
        head_re = re.compile('-HEAD-\r\n(.*?)\r\n^-[\w]+-', re.DOTALL+re.MULTILINE)
        title_re = re.compile(r'TITLE (\w+)')
        section_re = re.compile(r'Sec[s]*\. (\d{1}[ ,\w\-]{0,10})\.')
        subsection_re = re.compile(r'-STATUTE-(.*?)^-End-', re.DOTALL+re.MULTILINE)
        all_subsection_re = re.compile(r'^-[\w]{3,15}-(.*?)^-[\w]{3,15}-', re.DOTALL+re.MULTILINE)
        split_pattern = re.compile(r'^-[\w]{3,14}-',  re.MULTILINE)        
        if data:
            parts = data.split('-CITE-')
            #print "Total parts:", len(parts)
            i = 0
            levels = []
            failed = False
            divs_count = 0
            for part in parts:
                i += 1
                if i>1:
                    #print "Part %s"%i
                    try:
                        expcites = expcite_re.findall(part)[0].split("\r\n        ") # We need this because some title names splited into lines
                    except:
                        try:
                            expcites = expcite_re2.findall(part)[0].split("\r\n        ") # We need this because some title names splited into lines
                        except:
                            try:
                                expcites = expcite_re3.findall(part)[0].split("\r\n        ") # We need this because some title names splited into lines
                            except:
                                failed = True
                                print "Part failed:", part
                                self.text_log("Part failed:"+ part)
                                continue

                        new = True
                        #print expcites
                    else:
                        new = False

                    expcites = "".join(expcites)                                 # Next we join this splited names into one line
                    expcites = expcites.split("\r\n")
                    if new:
                        for exp in expcites:
                            if exp.strip()!="":
                                header = exp # this is for cases like http://uscode.house.gov/download/pls/02C20A.txt
                                               # in this file they break usual layout
                        #print header
                    j = 0
                    parent_title = False
                    for e in expcites:
                        j += 1
                        #print e
                        if j>1:
                            #print j
                            if not "Sec." in e and not "Secs." in e:
                                title_name = e.strip()
                                while "  " in title_name: # remove spaces
                                    title_name = title_name.replace("  "," ")

                                if title_name == "":
                                    continue
                                #print title_name
                            if j == 2:
                                
                                top_title_n = title_re.findall(title_name)[0]
                                top_title, c = Title.objects.get_or_create(title=top_title_n, name=title_name)
                                parent_title = top_title
                            elif j>2:
                                current_title, c = Title.objects.get_or_create(name=title_name, parent = parent_title)
                                parent_title = current_title
                    if not new:
                        header = head_re.findall(part)[0]#

                    header = unicode(header.strip().replace("\r\n", ""))
                    while "  " in header: # remove spaces
                        header = header.replace("  "," ")
                    
                    section = section_re.findall(header)
                    #if new:
                    #print "NEW=>>> Section ", section, header, expcites
                    if len(section)>0: # We found section:
                        section_id = section[0]
                        if len(header)>512:
                            print "Wrong section, skipping"
                            print header
                            self.text_log("Wrong section, skipping "+header )
                            continue
                        #print section_id
                        try:
                            section, c = Section.objects.get_or_create(section=section_id, top_title = top_title, title=current_title, header=unicode(header.replace("Sec.", u"§").replace("Secs.", u"§§")))
                        except:
                            print "----------------------------------"
                            print "Can't create section!"
                            print "Section: " , section, header
                            print "----------------------------------"
                            continue
                        else:
                            if c:
                                print "New section! %s" %section
                        try:
                            subsection_text = subsection_re.findall(part)[0]
                        except:
                            subsection_text = ""
                        ps = re.split(split_pattern, subsection_text)
                        # Parse subsections:
                        #subsection_start_re = re.compile(r"""^(?P<level>[ ]*)(?P<sub>\(\w+\))\s]+(?P<subsection_text>\w+)""", re.VERBOSE)
                        subsection_start_re = re.compile(r"""^(?P<level>[ ]*)
(?P<sub>\(\w+\)|\(\w+\)\(\w+\)
|\(\w+\)\(\w+\)\(\w+\)
|\(\w+\)\(\w+\)\(\w+\)\(\w+\)
|\(\w+\)\(\w+\)\(\w+\)\(\w+\)\(\w+\))[ ]+(?P<subsection_text>\w+)""", re.VERBOSE)
                        levels = {}
                        old_level = 0
                        c_subsection = {}
                        k = 0
                        sub = []
                        full_text = u""
                        level = 0
                        old_estimated_level = 0
                        old_real_level = 0
                        # Split section text into lines
                        last_line = ""
                        for line in ps[0].split("\r\n"):
                            #section_ref = found_sections(line.replace("\r\n", ""))
                            #if section_ref:
                            #    log.write(section_ref+"\r\n")

                            subsection_start = subsection_start_re.match(line) # Identify if this line is start of new subsection
                            try:
                                line = unicode(line.decode("windows-1252"))
                            except UnicodeDecodeError:
                                try:
                                    print "Error, can't convert to unicode - ", line
                                except:
                                    pass
                                line = unicode(line, errors='ignore')
                            
                            last_line = last_line.lower()
                            if last_line.endswith("subsection"): # some additional check for subsection start
                                subsection_start = None

                            if last_line.endswith("paragraph"): # some additional check for subsection start
                                subsection_start = None

                            if ((last_line.endswith(") or") or last_line.endswith(", or") or last_line.endswith("and")) and 
                                ("subsection" in last_line or "paragraph" in last_line)):
                                subsection_start = None


                            if subsection_start is not None:
                                #subsections_ = subsection_start.split(")") - we need this for weird subsections
                                #subsections_list = []
                                #for tmp_subs in subsections_:
                                #    if tmp_subs.strip()!="":
                                #        subsections_list.append(tmp_subs+")")
                                subsection_subs_re = re.compile(r'\(\w+\)')
                                #subsections_count = len(subsection_subs_re.findall())
                                #if subsection_count >1:
                                #    old_line = line
                                #    line = line.

                                k += 1
                                if len(line)<10: # Test if subsection text too short, possible error
                                    print line
                                    sys.exit()
                                real_level = len(subsection_start.group('level')) # real_level -count of spaces from start of line to text
                                if real_level == 4: # 4 spaces mean 1 level
                      
                                    level = 1
                                    levels = {1:real_level} # reset levels dict
                                    #if len(subsections_list)>1:# many levels in one line, example: "(a)(1)(A) The Sp"
                                        
                                else:
                                    #print "Old:%s New:%s"%(old_real_level, real_level)
                                    if real_level > old_real_level: # Next level
                                        level = old_level + 1
                                        levels[level] = real_level # Add this level to dictionary
                                        #print "New reallevel append - %s"%real_level
                                        #print levels
                                    elif old_real_level == real_level: # same level
                                        level = old_level
                                    else: # Now we need to calculate to which level we fall
                                        level = False
                                        for k in sorted(levels.keys()):
                                            if levels[k] == real_level:
                                                level = k
                                            #if levels[k] > real_level: # delete all levels lie over our level
                                            #    del levels[k]
                                        if not level: #Looks like this not real level
                                            #print "Level not found, levels = ", levels
                                            #print "real_level - ", real_level
                                            #print line
                                            
                                            subsection_start = None 
                                            #sys.exit()
                                            level = old_level
                                        else:
                                            for k in sorted(levels.keys()):
                                                if levels[k] == real_level:
                                                    level = k
                                                if levels[k] > real_level: # delete all levels lie over our level
                                                    del levels[k]
                                            
                            if subsection_start is not None:
                                #print "Real %s Old level %s Level %s Old_real %s" %( real_level, old_level, level, old_real_level)
                                old_real_level = real_level # save previous real level
                                #old_level = level # save previous level
                                #print sub

                                current_sub = subsection_start.group('sub')                                
                                if len(current_sub)>9:
                                    print "Weird sub: %s"%current_sub
                                    print line
                                    self.text_log("Weird self %s line- %s "%(current_sub, line) )
                                    #subsection_start = False
                                    #continue
                                    #sys.exit()

                                if old_level == level: # new element with same level
                                    #print sub
                                    #print c_subsection[level]
                                    subsection, c  = Subsection.objects.get_or_create(section=section, subsection = "".join(sub), 
                                                            text = c_subsection[level], part_id =k, level=level)
                                    subsection.save()                                   
                                    c_subsection[level] = ""
                                    if level == 1:
                                        sub = []
                                    else:
                                        sub = sub[:-1] # Remove last level sub
                                    sub.append(current_sub) # add new level sub
                                    
                                    
                                if old_level < level: # new element with same level                                    
                                    sub.append(current_sub) # add new level sub

                                if old_level > level: # new element with same level
                                    subsection, c = Subsection.objects.get_or_create(section=section, subsection = "".join(sub), 
                                                            text =c_subsection[level], part_id =k, level=level)
                                    #try:
                                    #    subsection.save()
                                    #except:
                                    #    print "".join(sub)
                                    #    print level
                                    #    print section
                                    #    sys.exit()

                                    c_subsection[level] = ""
                                    level_step = old_level-level+1
                                    #print "level step %s"%level_step
                                    sub = sub[:-level_step]
                                    sub.append(current_sub) # add new level sub

                                if old_level == level or old_level>level: # new element with same level
                                    if old_level>level:
                                        divs = u"</div>" * ((old_level - level)+1)+"<!-- next - new element old_level>level -->"
                                    else:
                                        divs = u"</div> <!-- next - new element old_level = level -->" 

                                    if level < 3:
                                        if full_text != "":
                                            full_text += u'%s<div id="%s" old_level = "%s" class="psection level%s"><span class="span_head">%s</span><br />' %(divs, "".join(sub), old_level, level, line)
                                        else:
                                            full_text += u'<div id="%s" class="psection level%s"><span class="span_head">%s</span><br />' %("".join(sub), level, line)
                                    else:
                                        if full_text != "":
                                            full_text += u'%s<div id="%s" class="psection level%s">%s<br />' %(divs, "".join(sub), level, line)
                                        else:
                                            full_text += u'<div id="%s" class="psection level%s">%s<br />' %("".join(sub), level, line)
                                else:
                                    #print "New level ->%s"%line
                                    if level > 2:
                                        full_text += u'<div id="%s" class="psection level%s">%s<br />' %("".join(sub), level, line)
                                    else:
                                        full_text += u'<div id="%s" class="psection level%s"><span class="span_head">%s</span><br />' %("".join(sub), level, line)                              


                                old_level = level

                            else:
                                full_text +=  line +"\r\n"

                            for l in range(0, level+1):
                                if c_subsection.has_key(level):
                                    c_subsection[l] = c_subsection[l] +"\r\n"+ line
                                else:
                                    c_subsection[l] = line

                            last_line = line
                        #print full_text
                        #print top_title.title
                        #print section.header
                        if level>1: # we need to close all open divs
                            #divs = "<!-- closing all divs old-level -level + 2 -->" + u"</div>" * ((old_level - level)+2)+ "<!-- end-->"
                            divs = "<!-- closing all divs level + 1 -->" + u"</div>" * level+ "<!-- end-->"
                            # old level = 5 level = 5   
                        elif level==1:
                            divs = "<!-- closing last div --></div><!-- end-->"
                        else:
                            divs = ""
                        if full_text.strip()!="":    
                            full_text += divs
                        section_header = unicode(section.header)
                        full_text = u'<div xmlns="http://www.w3.org/1999/xhtml"><h3>%s USC %s</h3> %s</div>'%(unicode(top_title.title), section_header, unicode(full_text))

                        #print full_text
                        #print levels
                        #sys.exit()
                        for l in levels:
                            subsection,c = Subsection.objects.get_or_create(section=section, subsection = "".join(sub), 
                                                    text =c_subsection[l], part_id =k, level=level)
                            #try:
                            #    subsection.save()
                            #except:
                            #    print "".join(sub)
                            #    print level
                            #    print section
                            #    sys.exit()


                        # Building section text from subsections
                        subsections = Subsection.objects.filter(section=section, subsection__isnull=True)
                        if len(subsections)==0:
                            subsection = Subsection(section=section, text = full_text)
                            subsection.save()
                            #sys.exit()
                        
                        #print all_subsections
                        k =0
                        
                        for p in ps: # additional information for section
                            k += 1
                            if k>1:
                                try:
                                    up = unicode(p)
                                    sa,c = SectionAdditional.objects.get_or_create(section=section, text=up, order=k)
                                except:
                                    
                                    pass
                        #print levels
                        #sys.exit()
            #log.close()                

    def handle(self, *args, **options):
        print "Start"
        #log = open("sections_ref.log", "w+")
        data,a,b = load_url(_START_URL)#"http://uscode.house.gov/download/pls/26C2.txt")
        links_re = re.compile(r'<A HREF="(.*?)">')
        sub_links_re = re.compile(r'<a href="(.*?)">(.*?)</a>')
        links = links_re.findall(data)
        for link in links:
            if "title" in link:
                subpage,a,b =load_url(_BASE_URL+link)
                sublinks = sub_links_re.findall(subpage)
                for sublink in sublinks:
                    if "Chapter" in sublink[1]:
                        page,a,b = load_url(_DOWNLOAD_URL+sublink[0])
                        if page:
                            print "Parsing: %s, from %s"%(sublink[1], sublink[0])
                            self.text_log("Parsing: %s, from %s"%(sublink[1], sublink[0]))
                            self.parse_chapter(page)
                        else:
                            print "Failed download pages %s"%sublink[0]

        
