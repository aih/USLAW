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
from urlparse import urljoin

from django.core.management.base import BaseCommand
from django.conf import settings

from utils.shorturl import bitly_short
from utils.load_url import load_url
from utils.txt2html import texttohtml
from laws.models import InternalRevenueManualToc, InternalRevenueManual
from parserefs.autoparser import parse 
from plugins.plugin_base import BasePlugin
from plugins.models import Plugin
from laws.views import target_to_section
from log.models import addlog

_PLUGIN_ID = 10

class Command(BaseCommand, BasePlugin):
    help = """Load and parse IRM from http://www.irs.gov/irm/"""
    sender = "IRM parser"

    def parse_content(self, sub_data, sub_url):
        """We have 2 type of regulations (s=1, s=2)
        1-st type is regulations like 1.xxx -
        2-nd - all others
        """
        
       
    def process_page(self, page):
        """
        Extract regulations links from page and process page
        """

        _BASE_URL = "http://www.irs.gov"
        new_urls = []
        if settings.DEBUG:
            print "Processing: %s" % page.url
            print "level: %s" % page.plugin_level
        data = page.page
        if page.plugin_level == 0:
            # at this level we just exctract links to Parts of IRM
            new_urls = []
            d = pq(data)
            items = d.items('tr')
            new_urls = []
            for i in items:
                href = i('p a').attr('href')
                toc = i('td:last').text()
                if href:
                    new_urls.append(["%s%s" % (_BASE_URL, href), 1])
            page.status = 1
            page.save()

        if page.plugin_level == 1:
            # sub pages with toc
            data = data.replace("&#160;", " ").replace(u' ', ' ')
            d = pq(data)
            title = d('h3:first').text().replace(u' ', ' ')
            print title
            top_toc_re = re.compile(r'Part (\d+)\.\s+(.*)')
            top_toc_parsed = top_toc_re.findall(title)[0]
            print top_toc_parsed
            if top_toc_parsed[1] == "":
                sys.exit()
            
            top_toc, c = InternalRevenueManualToc.objects.get_or_create(toc=top_toc_parsed[0],
                                                                        name=top_toc_parsed[1],
                                                                        level=0)
            top_toc.order_id = int(top_toc_parsed[0])
            top_toc.source_link = page.url
            top_toc.save()
            
            items = d.items('li')
            part_id = 0
            sub_toc_re = re.compile(r'(.*?)\s+(.*)')            
            for i in items:
                href = i('a').attr('href')
                b = i('b')
                if b: # TOC item without link:
                    sub_toc = b.text().replace(u' ', ' ')
                    sub_toc_parsed = sub_toc_re.findall(sub_toc)[0]
                    #print sub_toc_parsed
                    #print sub_toc
                    part_id += 1
                    sub_toc, c = InternalRevenueManualToc.objects.get_or_create(toc=sub_toc_parsed[0],
                                                                                name=sub_toc_parsed[1],
                                                                                parent=top_toc, level=1)
                    sub_toc.order_id = part_id
                    sub_toc.save()
                                
                else:
                    if href:
                        new_url = urljoin(page.url, href)
                        if settings.DEBUG:
                            print "New url %s" % new_url
                        part_id += 1
                        sub_toc2 = i.text().replace(u' ', ' ')
                        sub_toc_parsed = sub_toc_re.findall(sub_toc2)[0]
                        print sub_toc_parsed
                        sub_toc2, c = InternalRevenueManualToc.objects.get_or_create(toc=sub_toc_parsed[0],
                                                                                     name=sub_toc_parsed[1],
                                                                                     parent=sub_toc, level=2
                                                                                     )
                        sub_toc2.order_id = part_id
                        sub_toc2.source_link = new_url
                        sub_toc2.save()
                        new_urls.append([new_url, 2])
                        
                        #print href
                        #print i.text()
        if page.plugin_level == 2:
            data = data.replace('<div></div>', '') # PyQuery bug
            d = pq(data)
            fname = page.url.split('/')[-1].split('#')[0].split('?')[0]
            text = d('div.section:first').html().replace(fname, '')
            related_toc = InternalRevenueManualToc.objects.get(source_link=page.url)
            if settings.DEBUG:
                print related_toc.id
            irm, c = InternalRevenueManual.objects.get_or_create(toc=related_toc)
            nav_link_re = re.compile(r'<div class="chunkNavigation">(.*?)</div>', re.DOTALL)
            text = re.sub(nav_link_re, '', text)
            irm.text = text
            #print text
            irm.save()
            
        page.status = 1
        page.save()
        #print new_urls
        return new_urls


    def handle(self, *args, **options):
        _START_URLS = ["http://www.irs.gov/irm/",]
        self.run(_START_URLS, _PLUGIN_ID)

