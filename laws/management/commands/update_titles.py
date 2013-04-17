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


class Command(BaseCommand):
    help = """Import the US legal code TOC"""

    def handle(self, *args, **options):
        for t in Title.objects.all():
            t.save()
        for t in Section.objects.all():
            t.save()
            

