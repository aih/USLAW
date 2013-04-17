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
                if not filename.lower().endswith(".xml") or not 'TOC' in filename:
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
        with open(filename) as f:
            for l in f.readlines():
                if "<name>" in l: # title/name
                    name = name_re.findall(l)
                    title = title_re.findall(name[0])
                    if len(title)>0:
                        if "APPENDIX" in l: # APPENDIX
                            title_object = Title.objects.get(title = title[0]+'A', parent = None)
                        else:
                            title_object = Title.objects.get(title = title[0], parent = None)
                        title_found = True
                        if last == False:
                            last = title_object
                        
                    else:
                        subtitle_text = name[0]# Title.objects.get_or_create(title = title[0], parent = parent_object)
                        
                if "<hdsupnest" in l: # looking for level
                    supnest_found = True
                    supnest = hdsupnest_re.findall(l)
                    supnest_text = supnest[0][1]
                    title = title_re.findall(supnest_text)
                    if len(title)>0:
                        tree.append(title_object)
                    else:

                        parent = tree[-1] # last element
                        try:
                            last = Title.objects.get(name=supnest_text, parent=parent)
                            tree.append(last)
                        except Title.DoesNotExist:
                            print "Not found: %s parent - %s"%(supnest_text, parent)
                            print l
                            print filename
                            for t in tree:
                                print "Title:", t.title, "Name:", t.name, "ID:", t.id
                            sys.exit()

                else:
                    if supnest_found:
                        supnest_found = False
                        print "%s is under %s " %(subtitle_text, supnest_text)
                        #if supnest_text[:4] == "TITLE"[:4]: # title
                        #    parent = title_object #Title.objects.get(parent = None, title=title[0])
                        #    print "Parent: %s"%parent
                        #else:
                        #    parent,c  = Title.objects.get_or_create(name = supnest_text, parent=last)#, title=title_object.title)
                        last, c  = Title.objects.get_or_create(name=subtitle_text, parent = tree[-1])
                        last.save()
                        tree = []

                if "<sec refid=" in l:
                    sec_id = sec_re.findall(l)
                    try:
                        section =  sec_id[0][1]
                    except:
                        try:
                            sec_id = sec2_re.findall(l)
                            print sec_id[0][1]
                        except:
                            print l
                            print format_exc()
                            sys.exit()
                            raise
                    try:
                        if title_object.title=='40' and section =='1':
                            pass
                        else:
                            section_object = Section.objects.get(title=title_object, section=section)
                            #print section_object
                    except Section.DoesNotExist:
                        section = section.replace(' ', '_')
                        try:
                            section_object = Section.objects.get(title=title_object, section=section)
                        except Section.DoesNotExist:
                            section_n = section[:-1]+"-"+section[-1:]
                            section_n2 = section[:-2]+"-"+section[-2:]
                            section_n3 = section[:-3]+"-"+section[-3:]

                            try:
                                section_object = Section.objects.raw("select * from laws_section where replace(section, '-','') = '%s' and title_id=%s"%(section, title_object.id))[0]
                                print section_object
                            except:
                                print format_exc()
                                print l
                                print "NOT Found:", section, title_object
                                sys.exit()
                                    
                    section_object.subtitle = last
                    section_object.save()
