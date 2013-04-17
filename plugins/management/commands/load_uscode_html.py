# -*- coding: utf-8 -*-
# Load and parse US Code files from  http://uscode.house.gov/xhtml/

import re
#import gc
import sys
import traceback
import HTMLParser
#import BeautifulSoup
from optparse import make_option
from BeautifulSoup import BeautifulSoup, ICantBelieveItsBeautifulSoup
import BeautifulSoup as bsoup 
from datetime import datetime

from django.utils.html import strip_tags
from django.core.management.base import BaseCommand
from django.core.mail import mail_admins

from laws.models import *
from log.models import addlog
from plugins.models import Plugin, Update
from storeserver.models import Store, Link
from parserefs.autoparser import parse
#from plugins.plugin_base import BasePlugin

#from utils.load_url import load_url

_BASE_URLS = ["http://uscode.house.gov/xhtml/uscprelim/", ] 
#              "http://uscode.house.gov/xhtml/2010/",
#              "http://uscode.house.gov/xhtml/2009/",]

_BASE_URL = "http://uscode.house.gov/"
_PLUGIN_ID = 2 #  Unique plugin ID

class Command(BaseCommand):
    help = """Load and parse US Code from XHTML Source, 
provide only_download argument to download all files"""
    args = ''

    option_list = BaseCommand.option_list + (
        make_option('--url',
            dest='url',
            default=False,
            help='Parse only specified url'),
        )
    def get_string(self, tags):
        """
        This helper needed to procces whole text in given tag including subtags
        """
        parser = HTMLParser.HTMLParser()
        return " ".join([strip_tags(parser.unescape(unicode(t))) for t in tags])

    def parse_tstring(self, tstring, top_title, current_section, current_title):
        """Parse links in text"""
        parsed_tstring = parse(tstring)[0]
        replaces = {"ref-title-this": top_title.title, 
                   "ref-section-this":current_section.section, 
                   "ref-subsection-this": 'SUBSECTION', 
                    # current_section.section+"#"+current_sub,  
                   "ref-paragraph-this":"id-%s" % str(current_title.id), 
                   "ref-chapter-this":"id-%s" % str(current_title.id),  
                   "ref-subchapter-this":"id-%s" % str(current_title.id),
                    'width="700"':'', }
        for k, v in replaces.iteritems():
            parsed_tstring = parsed_tstring.replace(k, v)

        return parsed_tstring

    def load_temporary_subsection(self, tstring, top_title, current_section,
                                  current_title, s_level, s_order, s_type,
                                  subsection):
        """Load subsection to temporary table"""
        section_changed = False
        if subsection != '':
            print "Subsection: %s" % subsection
        try:
            Subsection.objects.get(section=current_section,
                                      subsection=subsection, level=s_level,
                                      part_id=s_order, raw_text=tstring)
        except Subsection.DoesNotExist: # Something changed
            section_changed = True
            #print "Section - %s was changed (Subsection), new subsection: %s" % (current_section, subsection)
        #  Save to temporary table
        subsection, c = TmpSubsection.objects.get_or_create(section=current_section, 
                                                         subsection=subsection, 
                                                         level=s_level, 
                                                         part_id = s_order, 
                                                         s_type=s_type)#, raw_text=tstring)

        parsed_string = self.parse_tstring(tstring, top_title=top_title, 
                                           current_section=current_section,
                                           current_title=current_title)
        subsection.text = parsed_string
        subsection.raw_text = tstring
        subsection.save()
        #if section_changed:
        #    print "Section was changed"
        return section_changed

    def load_temporary_additional_section(self, tstring, top_title, 
                                          current_section, 
                                          current_title, s_level,
                                          sa_order, sa_type):
        """Load AdditionSection to temporary table"""

        section_changed = False
        try:
            SectionAdditional.objects.get(section=current_section,
                                             order=sa_order, sa_type=sa_type,
                                             raw_text=tstring)
        except SectionAdditional.DoesNotExist:
            section_changed = True
            print "Section - %s was changed (additional section)" % current_section

        
        sa, c = TmpSectionAdditional.objects.get_or_create(section=current_section,
                                                     order=sa_order, sa_type=sa_type,
                                                     raw_text=tstring)

        parsed_tstring = self.parse_tstring(tstring, top_title=top_title, 
                                           current_section=current_section,
                                           current_title=current_title)
        sa.text = parsed_tstring
        sa.raw_text = tstring
        sa.save()
        return section_changed

    def update_from_tmp(self, section):
        """Move data from tmp table to main models"""

        print "Section %s was changed. Updating data... " % section

        Subsection.objects.filter(section=section).delete()
        for s in TmpSubsection.objects.filter(section=section):
            sub = Subsection(section=section, subsection=s.subsection,
                             level=s.level, part_id=s.part_id,
                             s_type=s.s_type, text=s.text,
                             raw_text=s.raw_text)
            sub.save()
        TmpSubsection.objects.filter(section=section).delete()

        SectionAdditional.objects.filter(section=section).delete()
        for s in TmpSectionAdditional.objects.filter(section=section):
            sa = SectionAdditional(section=section, order=s.order,
                                   text=s.text, raw_text=s.raw_text,
                                   publication_date=datetime.now(),
                                   sa_type=s.sa_type)
            sa.save()
        TmpSectionAdditional.objects.filter(section=section).delete()
        section.last_update = datetime.now()
        section.save()
        return None


    def parse_html(self, soup, additional=False, source=""):
        """This function parse given soup object and extract sections/titles/etc"""
        top_title_re = re.compile(r"TITLE (\d+\w{0,1})")
        section_re = re.compile(r"^\[{0,1}"+u"§"+"{1,2}(.*?)\.")
        section_re2 = re.compile(r"^\[{0,1}Rule\s(.*?)\.")
        section_re3 = re.compile(r"^\\\[{0,1}"+u"§"+"{1,2}(.*?)\\\.")
        section_re4 = re.compile(r"^"+u"§"+"(.*?) ") #  For sections like:
                                                     # §5302A\1\  Collection of indebtedness: 

        subsection_re = re.compile(r"^(\(\w{1,3}\))")

        section_started = False
        s_level = 0 # subsection level
        s_order = 0 # subsection order
        old_level = 0
        old_sub = ""
        subs_list = []
        parser = HTMLParser.HTMLParser()
        j = 0
        self_get_string = self.get_string # Some optimisations
        local_strip_tags = strip_tags     # Some optimisations
#        local_subsection_get_or_create = TmpSubsection.objects.get_or_create # Some optimisations
#        local_sectionadditional_get_or_create = TmpSectionAdditional.objects.get_or_create # Some optimisations
        plugin = Plugin.objects.get(plugin_id=_PLUGIN_ID)
        title_started = False
        chapter_started = False
        section_changed = False
        section_ended = False
        old_section = None
        current_section = None
        top_title_created = False
        top_title = False
        chapter_created = False
        current_title = False
        statute_body_started = False
        for t in soup.body.div:
            if isinstance(t, bsoup.Comment):
                if u'field-start:statute' in t:
                    statute_body_started = True
                if u'field-end:statute' in t:
                    statute_body_started = False

            if isinstance(t, bsoup.Tag): # Ok if this is a tag:
                if section_started:
                    title_started = False
                    chapter_started = False
                    
                if section_ended:
                    if old_section is None:
                        old_section = current_title
                    if section_changed: # Section was changed - update data
                        self.update_from_tmp(old_section)
                    
                    else: #  Check count of subsections (if subsection was deleted)
                        c = Subsection.objects.filter(section=old_section).count()
                        c_check = TmpSubsection.objects.filter(section=old_section).count()
                        if c != c_check:
                            print "Count of subsections diff: %s != %s" % (c, c_check)
                            self.update_from_tmp(old_section)
                        else:
                            c = SectionAdditional.objects.filter(section=old_section).count()
                            c_check = TmpSectionAdditional.objects.filter(section=old_section).count()
                            if c != c_check:
                                print "Count of section additional diff: %s != %s" % (c, c_check)
                                self.update_from_tmp(old_section)
                        TmpSubsection.objects.all().delete()
                        TmpSectionAdditional.objects.all().delete()
                    section_ended = False

                if (title_started and section_started == False) or \
                   (chapter_started and section_started == False): # here goes title text
                    if title_started:
                        if top_title_created or top_title.text == '':
                            if top_title.text is None:
                                top_title.text = ''
                            top_title.text = top_title.text + unicode(t)
                            top_title.save()
                        else:
                            #print "Title already have text, skipping update"
                            pass
                    elif chapter_started:
                        if chapter_created or current_title.text == '':
                            if current_title.text is None:
                                current_title.text = ''
                            current_title.text = current_title.text + unicode(t)
                            current_title.save()
                        else:
                            #print "Title already have text, skipping update"
                            pass
                    else:
                        raise
                    #print ">>", t
                    #print "---------------------------"
                    #print self_get_string(t.contents)
                    
                if t.name == "h1": # Title 1-st level
                    #try:
                    tstring = unicode(local_strip_tags(
                            self_get_string(t.contents)).replace('&mdash;', ' - ').replace(u"—", " - ")
                                      )
                    #except:# If there is no strong
                    try:
                        title_id = top_title_re.findall(tstring)[0]
                        if "APPENDIX" in tstring:
                            title_id += "A"
                    except IndexError:
                        #print "Top Title not found:", tstring
                        #print "Title does not exists: %s" % tstring
                        #print "Tag: %s" % t.name
                        #addlog(text="Title not found - %s tag - %s, source - %s " % (tstring, t.name, source), 
                        #       sender="plugin %s" % _PLUGIN_ID, level=2, sobject1="%s" % _PLUGIN_ID, sobject2="")
                        #raise
                        if top_title:
                            print "Using old top title: %s" % top_title
                            pass
                        else:
                            print "Top Title not found:", tstring
                            print "Title does not exists: %s" % tstring
                            raise
                    else:
                        try:
                            top_title = Title.objects.get(name=tstring, title=title_id)
                        except Title.DoesNotExist:
                            #print "Title does not exists: %s" % tstring
                            #print "Tag: %s" % t.name
                            top_title = Title(name=tstring, title=title_id)
                            top_title_created = True # For new titles - update Text
                        else:
                            top_title_created = False
                            if additional:
                                print "Skipp additional source"
                                return

                        top_title.int_title = 0
                        top_title.save()
                        print "title: %s" % top_title
                        u = Update(plugin=plugin, update_text="New Title Added -  %s " % top_title)
                        u.save()

                    section_started = False
                    chapter_started = False
                    title_started = True
                    #print title_id

                #if t.name == "h3": # Chapter
                #if 1 == 1
                # Tables:
                if t.name == "table" and section_started:
                    tstring = unicode(t)
                    if self.load_temporary_subsection(tstring=tstring, top_title=top_title, 
                                                      current_section=current_section,
                                                      current_title=current_title,
                                                      s_level=s_level, s_order=s_order, 
                                                      s_type=2, subsection=""):
                        section_changed = True #  Section was changed we need to move new subsections to main table

                if t.has_key("class"):
                    if t["class"] in ["chapter-head", "subchapter-head", "subpart-head",
                                      "part-head", "subtitle-head", ]:
                        section_started = False
                        chapter_started = True    
                        #old_chapter_level = chapter_level
                        
                    if t["class"] == "section-head":
                        tstring = unicode(local_strip_tags(self_get_string(t.contents)).replace('&mdash;', ' - ').replace(u"—", " - "))#parser.unescape(unicode(t.contents[0]))
                        
                        #print tstring
                        try:
                            section_id = section_re.findall(tstring.strip())[0]
                        except IndexError:
                            try:
                                section_id = section_re2.findall(tstring.strip())[0]
                            except IndexError:
                                try:
                                    section_id = section_re4.findall(tstring.strip())[0]
                                except IndexError:
                                    try:
                                        section_id = section_re3.findall(tstring.strip())[0]
                                    except IndexError:
                                        if "Form" in tstring:
                                            continue 
                                        print "Can't found section number:"
                                        print tstring
                                        addlog(text="Can't found section number - %s tag - %s, source - %s. Try another hack." % (tstring, t.name, source), 
                                               sender="plugin %s" % _PLUGIN_ID, level=1, sobject1="%s" % _PLUGIN_ID, sobject2="")

                                        tstring = tstring[0].strip()
                                        section_id = section_re.findall(tstring)[0]
                            #raise

                        old_section = current_section
                        current_section, c = Section.objects.get_or_create(section=section_id, 
                                                                           title=current_title, 
                                                                           top_title=top_title, 
                                                                           header=tstring)
                        current_section.source = source
                        current_section.save()

                        print "Parsing section %s" % current_section
                        if c: # New section!
                            u = Update(plugin=plugin, update_text="New section Added -  %s " % current_section)
                            u.save()

                        section_started = True
                        section_ended = True
                        sa_order = 0 # Additional  section order
                        s_order = 0 # subsection order
                        if self.load_temporary_subsection(tstring=tstring, 
                                              top_title=top_title, 
                                              current_section=current_section,
                                              current_title=current_title,
                                              s_level=s_level, s_order=s_order, 
                                              s_type=2, subsection=""):

                            section_changed = True
                        #print "New section %s" % current_section
                        subs_list = []
                        old_level = 0

                if t.name == "h4":
                    if t.has_key("class"):
                        if t["class"] == "note-head":
                            if section_started: #Additional section text , type = Header
                                tstring = self_get_string(t.contents)

                                if self.load_temporary_additional_section(
                                               tstring=tstring,
                                               top_title=top_title,
                                               current_section=current_section,
                                               current_title=current_title, 
                                               s_level=s_level, 
                                               sa_order=sa_order,
                                               sa_type=1):
                                    section_changed = True

                                sa_order += 1

                #if t.name=="p" or t: 

                if t.has_key('class'): # title text
                    #if t['class'] =='usc-title-ital-spanner':
                    #    try:
                    #        tstring = parser.unescape(unicode(" ".join(t.contents)))
                    #        top_title.text = tstring
                    #        top_title.save()
                    #    except:
                    #        pass

                    if section_started:
                        if (t['class'] =='note-body' \
                                or t["class"] == "source-credit") \
                                and statute_body_started == False:
                            tstring = self_get_string(t.contents) #parse(self.get_string(t.contents))[0]

                            if self.load_temporary_additional_section(
                                           tstring=tstring,
                                           top_title=top_title,
                                           current_section=current_section,
                                           current_title=current_title, 
                                           s_level=s_level, 
                                           sa_order=sa_order,
                                           sa_type=0):
                                section_changed = True
                            sa_order += 1
                        else:
                            pass 
                        if 'statutory-body' in t['class'] \
                                or t["class"] == "subsection-head" \
                                or t["class"] == "paragraph-head" \
                                or t["class"] == "subparagraph-head" \
                                or t["class"] == "clause-head" \
                                or statute_body_started: # New subsection
                            s_type = 0
                            if t['class'] == "subsection-head":
                                s_type = 1
                                s_level = 0
                            if t['class'] == "paragraph-head":
                                s_type = 1
                                s_level = 1
                            if t['class'] == "subparagraph-head":
                                s_type = 1
                                s_level = 2
                            if t['class'] == "clause-head":
                                s_type = 1
                                s_level = 3
                            if t['class'] == "subclause-head":
                                s_type = 1
                                s_level = 4

                            if t['class'] == 'statutory-body':
                                s_level = 0
                            if 'body-1em' in t['class']:
                                s_level = 1
                            if 'body-2em' in t['class']:
                                s_level = 2
                            if 'body-3em' in t['class']:
                                s_level = 3
                            if 'body-4em' in t['class']:
                                s_level = 4
                            if 'body-5em' in t['class']:
                                s_level = 5
                            #if "cap-smallcap" in t.contents:
                            #    s_type = 1
                            tstring = res = self_get_string(t.contents) #parse(self.get_string(t.contents))[0]
 
                            sub = subsection_re.findall(tstring)
                            if s_level == 0:
                                subs_list = []

                            if len(sub) > 0:
                                sub = sub[0]
                            else:
                                sub = ""
                            #print "Sub: %s, iteration: %s, section: %s, level %s old_level %s" %(sub, j, current_section.section, s_level, old_level)
                            j += 1
                            if sub == "":
                                current_sub = ""
                            else:
                                if s_level > old_level:
                                    subs_list.append(sub)

                                if s_level <= old_level:
                                    """
                                    Example:
                                        (a)             <- Level 0
                                           (1)          <- Level 1
                                               (i)      <- Level 2
                                           (2)          <- Level 1    
                                    subs_list = ['(a)',]            
                                    subs_list = ['(a)','(1)',]            
                                    subs_list = ['(a)','(1)',('i')]  <- Level 2
                                    delta = 1 - 2 - 1 = -2
                                    subs_list[:-1] = ['(a)','(2)']
                                    """
                                    delta = s_level - old_level - 1
                                    if delta == 0:
                                        delta = -1
                                    subs_list = subs_list[:delta]
                                    subs_list.append(sub)
                                current_sub = "".join(subs_list)

                                old_level = s_level
                                old_sub = current_sub
                                old_subs = subs_list
                            #print subs_list
                            s_order += 1 


                            if self.load_temporary_subsection(tstring=tstring, 
                                              top_title=top_title, 
                                              current_section=current_section,
                                              current_title=current_title,
                                              s_level=s_level, s_order=s_order,
                                              s_type=s_type, subsection=current_sub):
                                section_changed = True

            if isinstance(t, bsoup.Comment):
                """expcite:TITLE 1-GENERAL PROVISIONS!@!CHAPTER 1-RULES OF CONSTRUCTION"""
                tstring = unicode(t)
                
                if "expcite:" in tstring:
                    title_list = tstring.split("!@!") # we don't need first element
                    if len(title_list) > 1:
                        current_title = top_title
                        for title in title_list[1:]:
                            if not title.strip().startswith("Sec") and not title.strip().startswith("[") \
                                    and not title.strip().startswith("Rule") and not title.strip().startswith("[Rule"):
                                current_title, c = Title.objects.get_or_create(name=title.replace("-->","").replace("-"," - ").strip().replace('&mdash;', ' - '), parent=current_title)
                                if c:
                                    chapter_created = True
                                    print "new chapter/subchap/etc - %s" % current_title
                                    #print title
                                    #print tstring
                                    u = Update(plugin=plugin, update_text="New Title/Paragraph Added -  %s " % current_title)
                                    u.save()
                                else:
                                    chapter_created = False

        #  We also should parse last section
        if section_changed: # Section was changed - update data
            self.update_from_tmp(current_section)
        else: #  Clear temporary data
            TmpSubsection.objects.all().delete()
            TmpSectionAdditional.objects.all().delete()
        section_changed = False

    def process_page(self, page):
        self_parse_html = self.parse_html
        # ------------- LEVEL 1 ------------------
        if page.plugin_level == 0: # Top Level (base urls)
            download_urls_re = re.compile(r'<A HREF="(.{5,35})">\w+\.htm</A>')
            if _BASE_URLS.index(page.url)>0:
                additional = 1
            else:
                additional = 0

            new_urls = download_urls_re.findall(page.page)
            result_urls = []
            for u in new_urls:
                result_urls.append(["%s%s" % (_BASE_URL, u), 1, additional, "ISO-8859-1"]) # New URLs with Level = 1
            return result_urls # Return URLs for downloading
        # ------------- LEVEL 2 ------------------
        if page.plugin_level == 1: # Parse Page
            soup = ICantBelieveItsBeautifulSoup(page.page)
            if page.category_id == 0: # We use category_id for storing 'additional' parameter
                additional = False
            else:
                additional = True
            self_parse_html(soup, additional, page.url)
            return [] # No new URLs

    def handle(self, *args, **options):
        """
        Some examples:
        <h1 class="usc-title-head">TITLE 9&mdash;ARBITRATION</h1> - top title
        <h3 class="chapter-head"> - chapter 
        <h3 class="section-head"> - section 
        note-head
        <h4 class="subsection-head">
        <p class="statutory-body"> - section text
        <p class="statutory-body-1em"> - subsection level 2
        <p class="statutory-body-2em"> - subsection level 3
        <p class="statutory-body-3em"> - subsection level 4
        <p class="statutory-body-4em"> - subsection level 5
        <p class="statutory-body-5em"> - subsection level 6

        Test data:
        #data,a,b = load_url("http://uscode.house.gov/xhtml/2010/2010usc09.htm")#"http://uscode.house.gov/download/pls/26C2.txt")
        #data,a,b = load_url("http://uscode.house.gov/xhtml/2010/2010usc26.htm")

        """
        print "Start....."
        print

        # This block used only For tests
        if options["url"]:
            html_cache = UscodeHtml.objects.get(url=options['url'])
            data = html_cache.data
            try:
                soup = BeautifulSoup(data)
            except:
                print "Standard Soup fails"
                soup = ICantBelieveItsBeautifulSoup(data)
                self.parse_html(soup, False, options['url'])
            sys.exit()

        # Real Start

        plugin = Plugin.objects.get(plugin_id=_PLUGIN_ID)
        plugin.last_start = datetime.now()
        plugin.save()

        # Take some pages to process, for now only 1 page per start
        loaded = Store.objects.filter(plugin_id=_PLUGIN_ID, status=0)[:1] 
        loaded_count = len(loaded)
        new_links = []

        for l in loaded:
            try:
                print "Processing %s" % l.url
                result = self.process_page(l)                    
            except:
                print traceback.format_exc()
                result = False
                #  Now we should empty all temporary tables
                TmpSubsection.objects.all().delete()
                TmpSectionAdditional.objects.all().delete()
                er = str(traceback.format_exc())
                er = er + "\r\n Store page id: "+str(l.id)
                plugin.error = er
                plugin.save()
                addlog(text=er, sender=str(_PLUGIN_ID), level=2)
                mail_admins("Plugin %s Error" % _PLUGIN_ID, er)
                l.status = 2
                l.error = er
                l.save()

            if result != False:
                #print "Setting Status=1!"
                l.status = 1 #  Links processed
                l.save()
                for n in result:
                    if not "xhtml/uscprelim/usclass.htm" in n[0]: #  We should skip this file
                        nl = Link(url=n[0], plugin_id=_PLUGIN_ID, 
                                  plugin_level=n[1], status=0, 
                                  decode_charset=n[3], category_id=n[2])
                        nl.save()
                        nl.id = None
                new_links.append(result)

        # Now lets check if end with iteration and start from begining
        if len(new_links) == 0 and loaded_count == 0:
            links_count = Link.objects.filter(plugin_id=_PLUGIN_ID, status=0).count()
            if links_count == 0:  # We add start(initial) URLs for this plugin
                for url in _BASE_URLS:
                    l = Link(url=url, plugin_id=_PLUGIN_ID, plugin_level=0, 
                             url_type=0)
                    l.save()



