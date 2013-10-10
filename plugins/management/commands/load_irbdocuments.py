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

from django.core.management.base import BaseCommand
from django.conf import settings

from laws.models import InternalRevenueBulletinToc, InternalRevenueBulletin, IRBDocument
from parserefs.autoparser import parse 
from plugins.plugin_base import BasePlugin
from plugins.models import Plugin
from laws.views import target_to_section
from log.models import addlog

_PLUGIN_ID = 12

class Command(BaseCommand, BasePlugin):
    help = """Extract documents from IRB (from our database)"""
    sender = "IRB document extractor"

       
    
    def handle(self, *args, **options):
        dt = IRBDocument.DOCUMENT_TYPES
        document_type_regexps = (
            (r'Rev\. Proc\.(.*?)', dt[0][0]),
            (r'Announcement (\d+)(.*?)', dt[1][0]),
            (r'Notice(.*?)', dt[2][0]),
            (r'T\.D\.(.*?)', dt[3][0]),
            (r'REG\-(\d+)\-(.*?)', dt[4][0]),
            (r'Rev\. Rul\.(.*?)', 5),
            )
        irbs = InternalRevenueBulletin.objects.filter(toc__section_id__isnull=True)
        for irb in irbs:
            print irb.toc.section_id
            for reg in document_type_regexps:
                cr = re.compile(reg[0])
                res = cr.match(irb.toc.name)
                if res:
                    if reg[1] == 5: # Revenue Ruling
                        # skip for now, we need to deduplication procedure first
                        pass
                    else:
                        irbd, c = IRBDocument.objects.get_or_create(document_type=reg[1],
                                                                    irb=irb)
                        irbd.save()
                        if c:
                            print "New IRB Document: %s" % irbd
