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
from laws.views import target_to_section

class Command(BaseCommand):
    help = """Update sections top_title field for speed optimizations"""

    def handle(self, *args, **options):
        total = Section.objects.all().count()
        i = 0
        print "Updating top_title field for sections started."
        for t in Section.objects.all():
            i += 1
            t.top_title = t.get_title()
            t.save()
            if i%100 == 0:
                print "%s of %s completed" % (i, total)
