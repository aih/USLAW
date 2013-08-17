# -*- coding: utf-8 -*-
# Load named Statut from http://uscode.house.gov/popularnames/popularnames.htm

try:
    import re2 as re
except:
    import re
import os
import sys
from traceback import format_exc
from datetime import datetime

from django.core.management.base import BaseCommand
from django.conf import settings

from laws.models import Title, Section, NamedStatute
from laws.views import target_to_section
from utils.load_url import load_url
from parserefs.autoparser import parse

class Command(BaseCommand):
    help = """load named Statute from http://uscode.house.gov/popularnames/popularnames.htm"""

    def handle(self, *args, **options):
        url = "http://uscode.house.gov/popularnames/popularnames.htm"
        print "Loading data: %s " % url
        data, a, b = load_url(url)
        data = unicode(data.decode("iso-8859-1"))
        item_re = re.compile(r"<div class='popular-name-table-entry(.*?)</div>", re.DOTALL)
        name_re = re.compile(r'<popular-name>(.*?)</popular-name>', re.DOTALL)
        additional_re = re.compile(r'<p(.*?)>(.*?)</p>')
        link_re = re.compile(r'(\d+)\sU\.S\.C\.\s(\d\w*(?:\(\w+\))*)', re.IGNORECASE)
        i = 0
        items = item_re.findall(data)
        for item in items:
            i += 1
            name = name_re.findall(item)[0]
            print "-" * 50
            print "Item: %s" % i
            print "Popular name: %s " % name
            additionals = additional_re.findall(item)
            desc = ""
            for ai in additionals:
                desc = "%s\n%s" % (desc, ai[1])
            links = link_re.findall(desc)
            print desc
            section = None
            if len(links) > 0:
                print "Link to:", links[0]
                try:
                    title = Title.objects.get(title=links[0][0], parent__isnull=True)
                except Title.DoesNotExist:
                    pass
                else:
                    try:
                        section = Section.objects.get(top_title=title, section=links[0][1])
                    except Section.DoesNotExist: #  Some sections was omitted
                        print "Section not found: %s " % links[0][1]
                    except Section.MultipleObjectsReturned: #  Some sections 
                        print "Mutliple Sectiosn found: %s " % links[0][1]
            else:
                print 'Link not found'
            
            ns = NamedStatute(title=name, description = desc, section=section)
            ns.save()
            
