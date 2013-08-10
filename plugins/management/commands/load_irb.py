# -*- coding: utf-8 -*-
# Uslaw Project

try:
    import re2 as re
except ImportError:
    import re
from datetime import datetime
from time import strptime, mktime
import sys
import traceback
from pyquery import PyQuery as pq
from urlparse import urljoin

from django.core.management.base import BaseCommand
from django.conf import settings

from utils.shorturl import bitly_short
from utils.load_url import load_url
from utils.txt2html import texttohtml
from laws.models import InternalRevenueBulletinToc, InternalRevenueBulletin
from parserefs.autoparser import parse 
from plugins.plugin_base import BasePlugin
from plugins.models import Plugin
from laws.views import target_to_section
from log.models import addlog

_PLUGIN_ID = 11

class Command(BaseCommand, BasePlugin):
    help = """Load and parse IRM from http://www.irs.gov/irm/"""
    sender = "IRB parser"

       
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
            # at this level we just exctract links to Parts of IRB
            new_urls = []
            d = pq(data)
            items = d.items('tr')
            new_urls = []
            for i in items:
                #print i
                html_href = i('td:first a:first').attr('href')
                pdf_href = i('td:first a:last').attr('href')
                if not html_href:
                    continue
                url = "%s%s" % (_BASE_URL, html_href)
                pdf_url = "%s%s" % (_BASE_URL, pdf_href)
                new_urls.append([url, 1])
                #new_urls.append([pdf_url, 5])

                pub_date = i('td:last').text()
                pub_date = strptime(pub_date, "%B %d, %Y")
                pub_date = datetime.fromtimestamp(mktime(pub_date))
                try:
                    irbtoc = InternalRevenueBulletinToc.objects.get(source_link=url)
                except InternalRevenueBulletinToc.DoesNotExist:
                    irbtoc = InternalRevenueBulletinToc(source_link=url,
                                                        pdf_link=pdf_url,
                                                        level=0, name="",
                                                        order_id=0,
                                                        current_through=pub_date,
                                                        element_type=0)
                    irbtoc.save()
            page.status = 1
            page.save()

        if page.plugin_level == 1:
            # sub pages with toc
            #data = data.replace("&#160;", " ").replace(u' ', ' ')
            top_irb_toc = InternalRevenueBulletinToc.objects.get(source_link=page.url)
            d = pq(data)
            title = d('h3:first').text().replace(u' ', ' ')
            title = ' '.join(title.split())
            top_irb_toc.name = title
            top_irb_toc.save()
            
            print title
            
            items = d.items('li')
            part_id = 0
            sub_part_id = 0 
            for i in items:
                href = i('a:first').attr('href')
                name = i('a:first').text().strip()
                name = ' '.join(name.split())
                url = urljoin(page.url, href)
                print "%s -> %s" % (name, url)
                if href.startswith('pt'): # new toc item
                    part_id += 1
                    irb_toc, c = InternalRevenueBulletinToc.objects.get_or_create(source_link=url,
                                                                                  parent=top_irb_toc,
                                                                                  name=name,
                                                                                  level=1, element_type=0)

                    irb_toc.part_id = part_id
                    irb_toc.save()
                    print "New irb toc: %s" % irb_toc
                    #new_urls.append([url, 2]) # FIXMEE
                elif href.startswith('ar') and not "#" in href: # level=2
                    part_id += 1
                    #url = urljoin(page.url, href)
                    sub_irb_toc, c = InternalRevenueBulletinToc.objects.get_or_create(source_link=url,
                                                                                  parent=irb_toc,
                                                                                  name=name,
                                                                                  level=2, element_type=1)
                    sub_irb_toc.part_id = part_id
                    sub_irb_toc.save()
                    print "New sub irb toc: %s" % sub_irb_toc
                    new_urls.append([url, 2])
                else:
                    if "#" not in href:
                        raise "Weird link, please fixme"
                    
                    sub_part_id += 1
                    #url = urljoin(page.url, href)
                    section_id = href.split('#')[1]
                    sub_sub_irb_toc, c = InternalRevenueBulletinToc.objects.get_or_create(source_link=url,
                                                                                          parent=sub_irb_toc,
                                                                                          name=name,
                                                                                          level=3, 
                                                                                          section_id=section_id,
                                                                                          element_type=2)
                    sub_sub_irb_toc.part_id = sub_part_id
                    sub_sub_irb_toc.save()
                    print "New sub sub irb toc: %s" % sub_sub_irb_toc
                    #new_urls.append([url, 2])
                    
                
        if page.plugin_level == 2:
            pass
            
        #page.status = 1
        #page.save()
        print new_urls
        return new_urls


    def handle(self, *args, **options):
        _START_URLS = ["http://www.irs.gov/irb/",]
        self.run(_START_URLS, _PLUGIN_ID)

