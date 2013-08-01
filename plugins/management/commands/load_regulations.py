# -*- coding: utf-8 -*-
# Uslaw Project
# Load regulations from http://ecfr.gpoaccess.gov/cgi/t/text/text-idx?c=ecfr&tpl=/ecfrbrowse/Title26/26tab_02.tpl
# 

try:
    import re2 as re
except ImportError:
    import re
from datetime import datetime
import sys
import traceback
from pyquery import PyQuery as pq

from django.core.management.base import BaseCommand
from django.conf import settings

from utils.shorturl import bitly_short
from utils.load_url import load_url
from utils.txt2html import texttohtml
from laws.models import Regulation, Section, Title
from parserefs.autoparser import parse 
from plugins.plugin_base import BasePlugin
from plugins.models import Plugin
from laws.views import target_to_section
from log.models import addlog

_PLUGIN_ID = 1

class Command(BaseCommand, BasePlugin):
    help = """Load and parse regulations from ecfr.gpoaccess.gov"""
    sender = "Regulation parser"

    def parse_content(self, sub_data, sub_url):
        """We have 2 type of regulations (s=1, s=2)
        1-st type is regulations like 1.xxx -
        2-nd - all others
        """

        if settings.DEBUG:
            print "Parsing regulation, url: %s " % sub_url
        title = Title.objects.get(title='26')
        content_re = re.compile(r'<h5>(.*?)</p>[ ]*</p>[ ]*<span>', re.DOTALL+re.IGNORECASE)
        content = content_re.findall(sub_data)
        content_founded = False

        if len(content) == 1:
            content = "<h5>"+content[0]+"</p></p>"
            content_founded = True
        if not content_founded:
            content_re = re.compile(r'<h5>(.*?)</EDNOTE></p>', re.DOTALL+re.IGNORECASE)
            content = content_re.findall(sub_data)
            if len(content)==1:
                content = "<h5>"+content[0]+"</EDNOTE></p>"
                content_founded = True
        if not content_founded:
            content_re = re.compile(r'<h5>(.*?)</p>[ ]*</font></p>', re.DOTALL+re.IGNORECASE)
            content = content_re.findall(sub_data)
            if len(content) == 1:
                content = "<h5>"+content[0]+"</p></font></p>"
                content_founded = True            
        if not content_founded:
            content_re = re.compile(r'<h5>(.*?)</DIV></DIV></p>', re.DOTALL+re.IGNORECASE)
            content = content_re.findall(sub_data)
            if len(content) == 1:
                content = "<h5>"+content[0]+"</div></div></p>"
                content_founded = True            

        if not content_founded:
            content_re = re.compile(r'<h5>(.*?)</p>[ ]*</p><br>', re.DOTALL+re.IGNORECASE)
            content = content_re.findall(sub_data)
            if len(content) == 1:
                content = "<h5>"+content[0]+"</p></p>"
                content_founded = True            

        if not content_founded:
            content_re = re.compile(r'<h5>(.*?)</PSPACE></font></p>', re.DOTALL+re.IGNORECASE)
            content = content_re.findall(sub_data)
            if len(content) == 1:
                content = "<h5>"+content[0]+"</PSPACE></font></p>"
                content_founded = True            

        if not content_founded:
            print "Can't extract content - %s" % sub_url
            #print sub_data[0]
            print "--------------------"
            #print content
            print
            return False

        header_re = re.compile(r'<h5>(.*?)</h5>')
        headers = header_re.findall(content)

        if len(headers) == 0:
            print "Can't find header %s" % sub_url
            print content[:20]
            sys.exit(2)
        header = headers[0]
        #print "Header - %s"%header
        regulation_re = re.compile(r'&#167;&nbsp;(.*?)&nbsp;')
        regulation = regulation_re.findall(header)
        reg_name_re = re.compile(r'&nbsp;&nbsp;&nbsp;(.*)')
        reg_name = reg_name_re.findall(header)[0]
        if len(regulation) != 1:
            print "Can't extract regulation number %s" % header
            sys.exit(2)
        regulation = regulation[0]
        #print regulation, reg_name
        content = unicode(content).replace('&#167;', u'§')
        r, c = Regulation.objects.get_or_create(section=regulation)
        print "Regulation: %s " % r.section
        if c: # New regulation!
            plugin = Plugin.objects.get(plugin_id=_PLUGIN_ID)
            #u = Update(plugin=plugin, update_text="New regulation Added -  %s " % r)
            #u.save()
            r.publication_date = datetime.now()
            r.last_update = datetime.now()
            r.shortlink = bitly_short(sub_url)

        else:
            r.shortlink = bitly_short(sub_url)
                
        current_through_re = re.compile(r'<STRONG>e-CFR Data is current as of (.*?)</STRONG>')

        try:
            current_through_data = current_through_re.findall(sub_data)[0].strip()
        except IndexError:
            print sub_data
            print "Can't extract current_through_ date"
            return False

        current_through = datetime.strptime(current_through_data, '%B %d, %Y')

        r.current_through = current_through
        #print r.current_through
        r.section = regulation
        r.title = reg_name
        r.last_update = datetime.now()
        if r.text != content:
            plugin = Plugin.objects.get(plugin_id=_PLUGIN_ID)
            #u = Update(plugin=plugin, update_text="Regulation text updated -  %s " % r)
            #u.save()

        r.text = content
        r.link = sub_url
        r.save()

        section_re = re.compile(r'([\w\d]+)\.(\d+)(.*?)([\(\)\-\w]*)')  # TODO: parse sections in another script?
        sect = section_re.findall(regulation)[0]
        #print "Part %s"%sect[0]
        part = sect[0]
        section_number = sect[1]

        if part == '1': # Regulations start with 1, simple case
            try:
                section = Section.objects.get(top_title=title, section=section_number)
            except Section.DoesNotExist:
                pass
            else:
                r.main_section = section
                r.save()

        elif part in ['31', '35', '35a', '36', '52', '53', '54', 
                      '56', '141', '145', '156', '157', '301', 
                      '305', '404', '701', '702']: #Hardcoded parts 
            if part == '4':
                section_number = '954'
            elif part == '8':
                section_number = '2055'
            elif part == '9':
                section_number = '46'
                try:
                    section = Section.objects.get(top_title=title, section=section_number)
                except Section.DoesNotExist:
                    pass
                else:
                    r.sections.add(section)
                section_number = '38'
            elif part == '143':
                section_number = '4941'
            elif part == '148':
                section_number = '4216'
            elif part == '403':
                section_number = 7326

            try:
                section = Section.objects.get(top_title=title, section=section_number)
            except Section.DoesNotExist:
                pass
            else:
                r.main_section = section
                r.save()

        # Now we try to extract all references to sections:
        section_ref_re = re.compile(r'section (\d+)')
        sections = section_ref_re.findall(content)
        for s in sections:
            addlog("Section found - %s \r\n at %s  " % (s, sub_url), sender=self.sender, sobject1=unicode(r)[:20], sobject2=s[:20])
            try:
                section = Section.objects.get(top_title=title, section=s)
            except Section.DoesNotExist:
                pass
            except Section.MultipleObjectsReturned:
                sections = Section.objects.filter(top_title=title, section=s)
                for s in sections:
                    r.sections.add(s)
            else:
                r.sections.add(section)

        if len(sections) == 0:
            addlog("No sections found for %s" % sub_url, level=1, sender=self.sender, sobject1=unicode(r)[:20], sobject2= "No sections")

    def process_page(self, page):
        """
        Extract regulations links from page and process page
        """

        _BASE_URL = "http://www.ecfr.gov/"
        if settings.DEBUG:
            print "Processing: %s" % page.url
            print "level: %s" % page.plugin_level
        data = page.page
        base_re = re.compile(r'<td ALIGN="right" VALIGN="top"><a href="(.*?)"')
        new_urls = []
        if page.plugin_level == 0: # On this level goes links!
            d = pq(data)
            urls = d.items('td a.tpl')
            #urls = base_re.findall(data)
            for u in urls:
                #print u
                url = "%s%s" % (_BASE_URL, u.attr('href'))
                new_urls.append([url, 1])
            #print "New urls founded ", new_urls
            page.status = 1
            page.save()
            return new_urls

        if page.plugin_level == 1: #suburls
            d = pq(data)
            sub_urls = d.items('td a.tpl')
            
            tpl = False
            for s in sub_urls:
                if s.attr('href') is None:
                    #if settings.DEBUG:
                        #print "Skiping %s" % s
                    continue # skip some empty links
                print "S>", s
                url = "%s%s" % (_BASE_URL, s.attr('href'))
                if s.attr('href')[-3:] == "tpl": # url with a list of urls =)
                    new_urls.append([url, 1])
                else:
                    new_urls.append([url, 2])
            #else:
            #    print "No new urls founded"
                
            page.status = 1
            page.save()
            if settings.DEBUG:
                print new_urls
            return new_urls
            
                
        if page.plugin_level == 2: # content
            if settings.DEBUG:
                print "%" * 20
                print "processing content"
                print "%" * 20
            try:
                self.parse_content(page.page, page.url)
            except:
                addlog("Error parsing - %s \r\n %s" % (page.url, traceback.format_exc()), level=2, sender=self.sender)
                page.status = 2
                page.error = "Error parsing - %s \r\n %s" % (page.url, traceback.format_exc())
                page.save()
                print "Error parsing - %s \r\n %s" % (page.url, traceback.format_exc())
                return False
        return new_urls

    def handle(self, *args, **options):
        _START_URLS = ["http://ecfr.gpoaccess.gov/cgi/t/text/text-idx?c=ecfr&tpl=/ecfrbrowse/Title26/26tab_02.tpl",]
        self.run(_START_URLS, _PLUGIN_ID)

