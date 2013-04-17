"""Load USC 26 topics from TXT File"""
import sys, os

try:
    import re2 as re
except:
    import re
from django.core.management.base import BaseCommand

from laws.models import Section, Title, USCTopic

class Command(BaseCommand):
    help = """"Load USC 26 topics from TXT File"""

    #@transaction.commit_manually
    def handle(self, *args, **options):
        title_26 = Title.objects.get(title='26')
        topics_re = re.compile(r'(\w+)-(\w+)[\s]+(.*?)$')
        f = open("data/usc_topics.txt", "r")
        j = 0
        for l in f.readlines():
            
            data = topics_re.findall(l)[0]
            try:
                first_section = Section.objects.get(section=data[0], top_title=title_26)
            except Section.DoesNotExist:
                print "Section not found %s" % data[0]
                first_section = False
            try:
                last_section =  Section.objects.get(section=data[1], top_title=title_26)
            except Section.DoesNotExist:
                print "Section not found %s" % data[1]
                last_section = False
            if first_section and last_section:
                j += 2
                t, c = USCTopic.objects.get_or_create(first_section=first_section,
                                                   last_section=last_section,
                                                   name = data[2], order=j)
                if c:
                    print "New Topic created: %s " % t
            #print data[0]
            #print first_section, last_section
        f.close()



