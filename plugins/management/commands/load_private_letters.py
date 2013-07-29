# -*- coding: utf-8 -*-
# Uslaw Project
# Load rulings from http://www.irs.gov/pub/irs-wd/
# 

try:
    import re2 as re
except ImportError:
    import re
from datetime import datetime
from pyquery import PyQuery as pq
            
from django.core.management.base import BaseCommand
from django.conf import settings

from utils.load_url import load_url
from utils.txt2html import texttohtml
from laws.models import IRSPrivateLetter
from parserefs.autoparser import parse 
from plugins.plugin_base import BasePlugin
from utils.txt2html import texttohtml


_PLUGIN_ID = 4

class Command(BaseCommand, BasePlugin):
    help = """Load and parse PDF's from http://www.irs.gov/pub/irs-wd/"""
    sender = "Regulation parser"

    def process_page(self, page):
        """
        Extract letters from page and process page
        """
        _BASE_URL = "http://www.irs.gov/pub/irs-wd/"
        new_urls = []

        #  Level 0
        if page.plugin_level == 0: #  Top page
            parsed = pq(page.page)
            pdfs = parsed.items('td a')
            for p in pdfs:
                if p.attr('href').endswith(".pdf"):
                    nu = "%s%s" % (_BASE_URL, p.attr('href'))
                    #print nu
                    new_urls.append([nu, 1])
            dates_re = re.compile(r'<td align="right">(\d{2})-(\w{2,5})-(\d{4})')
            dates = dates_re.findall(page.page)
            max_date = False
            for d in dates:
                new_date = datetime.strptime("%s-%s-%s" % (d[0], d[1], d[2]), '%d-%b-%Y')
                if max_date:
                    if new_date > max_date:
                        max_date = new_date
                else:
                    max_date = new_date
            if settings.DEBUG:
                print "Current_Through: %s " % max_date
            IRSPrivateLetter.objects.all().update(current_through=max_date)
            return new_urls

        #  Level 1
        if page.plugin_level == 1: #  Pdf page
            print "PDF!, %s" % page.url
            data, a, b = load_url(page.url) #  We load url again because django do not support blob fields
            filename = page.url.split('/')[-1].split('#')[0].split('?')[0]
            number = filename[3:-4]
            full_filename = '%suploads/%s' % (settings.MEDIA_ROOT, filename)
            text_path = "%s.txt" % full_filename

            data = self.pdftotext(full_filename, text_path, data)
            data = parse(texttohtml(data))[0]
            data = self.replace_this_links(data)

            document = "uploads/%s" % filename
            pr, c = IRSPrivateLetter.objects.get_or_create(section=number, title=number)
            pr.document = document
            pr.text = data
            pr.link = page.url
            pr.last_update = datetime.now()
            pr.save()
            print "ID: %s" % pr.id
            self.extract_references(data, fai)

        return new_urls

    def handle(self, *args, **options):
        _START_URLS = ["http://www.irs.gov/pub/irs-wd/", ]
        self.run(_START_URLS, _PLUGIN_ID)
