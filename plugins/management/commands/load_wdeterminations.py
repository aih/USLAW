# -*- coding: utf-8 -*-
# Uslaw Project
# Load Written Determinations
# 

try:
    import re2 as re
except ImportError:
    import re
from datetime import datetime

from django.core.management.base import BaseCommand
from django.conf import settings

from utils.load_url import load_url
from utils.txt2html import texttohtml
from laws.models import WrittenDetermination, TextStore
from parserefs.autoparser import parse 
from plugins.plugin_base import BasePlugin

_PLUGIN_ID = 9
_DEBUG = True

class Command(BaseCommand, BasePlugin):
    help = """Load and parse Written Determinations """
    sender = "WrittenDetermination parser"

    def process_page(self, page):
        """
        Extract letters and process page
        """
        _BASE_URL = "http://www.irs.gov/"
        new_urls = []

        #  Level 0. This plugin have only 1 level
        if page.plugin_level == 0: #  Top page
            # First we extract next page
            if _DEBUG:
                print "Processing page: %s " % page.url
            next_page_re = re.compile(r'<a href="(.*?)">Next')
            try:
                next_page_link = next_page_re.findall(page.page)[0]
            except IndexError:
                if _DEBUG:
                    print "Looks like this is last page"
            else:
                next_page = "%s%s" % (_BASE_URL, next_page_link.replace("&amp;", "&"))
                new_urls.append([next_page, 0])
                """
                """
            documents_re = re.compile(r'<tr class="[\w]+">[\s]*<td class="LeftCellSpacer">[\s]*<a href="(?P<url>.*?)">(?P<product_number>.*?)</a>[\s]*</td>[\s]*[\s]*<td class="MiddleCellSpacer">(?P<uilc>.*?)</td>[\s]*<td class="MiddleCellSpacer">(?P<title>.*?)</td>[\s]*<td class="EndCellSpacer">(?P<external_publication_date>.*?)</td>[\s]*</tr>', re.DOTALL)
            documents = documents_re.findall(page.page)
            for d in documents:
                try:
                    print "Processing: %s " % d[2].strip()
                except (UnicodeEncodeError, UnicodeDecodeError):
                    pass
                external_publication_date = datetime.strptime(d[4].strip(), '%m/%d/%Y')
                data, a, b = load_url(d[0]) #  
                filename = d[0].split('/')[-1].split('#')[0].split('?')[0]
                full_filename = '%suploads/%s' % (settings.MEDIA_ROOT, filename)
                text_path = "%s.txt" % full_filename

                data = self.pdftotext(full_filename, text_path, data)
                data = parse(texttohtml(data))[0]
                data = self.replace_this_links(data)

                document = "uploads/%s" % filename

                fai, c = WrittenDetermination.objects.get_or_create(link=d[0].strip(),
                                                                    product_number=d[1].strip(),
                                                                    title=d[3].strip(),
                                                                    uilc=d[2].strip()) 
                fai.document = document
                fai.external_publication_date = external_publication_date.date()
                fai.last_update = datetime.now()
                fai.save()

                if fai.store is None:
                    ts = TextStore(text=data)
                    ts.save()
                    fai.store = ts
                    fai.save()

                self.extract_references(data, fai)

            return new_urls

        return new_urls

    def handle(self, *args, **options):
        _START_URLS = ["http://www.irs.gov/app/picklist/list/writtenDeterminations.html",]
        self.run(_START_URLS, _PLUGIN_ID)

