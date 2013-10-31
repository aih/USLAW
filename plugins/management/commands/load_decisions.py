# -*- coding: utf-8 -*-
# Uslaw Project
# Load Actions on Decisions (AOD) from http://www.irs.gov/app/picklist/list/actionsOnDecisions.html
# 

try:
    import re2 as re
except ImportError:
    import re
from datetime import datetime
import traceback

from django.core.management.base import BaseCommand
from django.conf import settings

from utils.load_url import load_url
from utils.txt2html import texttohtml
from laws.models import Decision, TextStore
from parserefs.autoparser import parse 
from plugins.plugin_base import BasePlugin


_PLUGIN_ID = 7
_DEBUG = True

class Command(BaseCommand, BasePlugin):
    help = """Load and parse Actionsondecisions
from http://apps.irs.gov/app/picklist/list/actionsOnDecisions.html"""
    sender = "Actionsondecisions parser"

    def process_page(self, page):
        """
        Extract publications and process page
        """
        _BASE_URL = "http://apps.irs.gov/"
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

            documents_re = re.compile(r'<tr class="[\w]+">[\s]*<td class="LeftCellSpacer">[\s]*<a href="(?P<url>.*?)">(?P<product_number>.*?)</a>[\s]*</td>[\s]*<td class="SecondColumnSpacer">(?P<title>.*?)</td>[\s]*<td class="MiddleCellSpacer">(?P<des>.*?)</td>[\s]*<td class="EndCellSpacer">(?P<external_publication_date>.*?)</td>[\s]*</tr>', re.DOTALL)
            documents = documents_re.findall(page.page)
            for d in documents:
                try:
                    print "Processing: %s " % d[2].strip()
                except (UnicodeEncodeError, UnicodeDecodeError):
                    pass
                try:
                    external_publication_date = datetime.strptime(d[4].strip(), '%m/%d/%Y')
                except ValueError:
                    print "Can't found external date - %s" % d[4]
                    print "FIX it mannualy!"
                    external_publication_date = datetime.strptime('01/01/1900', '%m/%d/%Y')
                    
                if settings.DEBUG:
                    print "Loading %s" % d[0]
                data, a, b = load_url(d[0], do_quote=True) #  We load url again because django do not support blob fields
                if not data:
                    print "Can't download %s" % d[0] # FIXME: add some logs here, etc
                    print a
                    print b
                filename = d[0].split('/')[-1].split('#')[0].split('?')[0]
                full_filename = '%suploads/%s' % (settings.MEDIA_ROOT, filename)
                text_path = "%s.txt" % full_filename
                f = open(full_filename, mode="wb")
                try:
                    f.write(data)
                    f.close()
                except:
                    print "Something wrong... file %s " % full_filename
                    print traceback.format_exc()
                    
                data = self.pdftotext(full_filename, text_path, data)
                if not data:
                    continue
                raw_data = texttohtml(data)
                data = parse(raw_data)[0]
                data = self.replace_this_links(data)

                document = "uploads/%s" % filename

                fai, c = Decision.objects.get_or_create(link=d[0].strip(), 
                                                        product_number=d[1].strip(),
                                                        title=d[2].strip())
                fai.document = document
                fai.description = d[3].strip()
                fai.external_publication_date = external_publication_date.date()
                fai.last_update = datetime.now()
                if fai.store is None:
                    st = TextStore(text=data, raw_text=raw_data)
                    st.save()
                    fai.store = st
                else:
                    fai.store.text = data
                    fai.store.raw_text = raw_data
                    fai.store.save()
                fai.save()
                fai.store.save()

                self.extract_references(data, fai)

            return new_urls

        return new_urls

    def handle(self, *args, **options):
        _START_URLS = ["http://apps.irs.gov/app/picklist/list/actionsOnDecisions.html",]
        self.run(_START_URLS, _PLUGIN_ID)
