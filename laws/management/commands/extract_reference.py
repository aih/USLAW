# -*- coding: utf-8 -*-
try:
    import re2 as re
except:
    import re
import os
import sys
import lxml.etree
from traceback import format_exc
from datetime import datetime
import gc
from optparse import make_option

from django.core.management.base import BaseCommand
from django.utils.encoding import force_unicode
from django.conf import settings
from django.db import connection, transaction

from laws.models import Title, Section, Subsection, SectionAdditional
from laws.views import target_to_section

from parserefs.autoparser import parse

class Command(BaseCommand):
    help = """Extract reference objects from Tax law documents"""

    option_list = BaseCommand.option_list + (
        make_option('--clear',
            action='store_true',
            dest='clear',
            default=False,
            help='Clear processed attribute'),
        make_option('--update-cache',
            action='store_true',
            dest='update-cache',
            default=False,
            help='Clear cache referenced table'),
        make_option('--steps',
            dest='steps',
            default=5,
            help='Count of steps processed per run'),
        )

    def clear(self):
        cursor = connection.cursor()
        # Data modifying operation - commit required
        # We use raw SQL, because for this simple operation it is 100x faster
        cursor.execute("update laws_section set is_processed=False;")
        transaction.commit_unless_managed()

    def update_cache_references(self):
        """Reference_sections table used for most_referenced statutes page
        Once a day or less we need to update this cache table"""
        cursor = connection.cursor()
        cursor.execute("delete from reference_sections") #  
        transaction.commit_unless_managed()
        cursor.execute("""insert into reference_sections 
                           (from_section_id, to_section_id) 
                            select a.section_id, b.section_id 
                              from laws_section_reference_subsection a, laws_subsection b 
                             where a.subsection_id =b.id;
                       """)
        transaction.commit_unless_managed()

    def handle(self, *args, **options):
        """
        We extract all links from subsections and add reference links
        """
        if options['clear'] == True: #  Clear processed attribute
            self.clear()
        elif options['update-cache'] == True:
            self.update_cache_references()
        else:
            fraction = 1000
            secs = Section.objects.filter(is_processed=False).count()
            if secs == 0: #  All processed
                sys.exit(0) #  Finished

            total_steps = secs/fraction + 2
            steps = options['steps']
            print "-" * 70
            print "\x1b[31m Total sections: %s, total steps: %s, steps per run: %s \x1b[0m" % (secs, total_steps, steps)
            print "-" * 70
            ref = re.compile(r'<a href="/laws/target/(.*?)"')

            for section in Section.objects.filter(is_processed=False).order_by("id")[:steps*fraction]:
                #print "\x1b[31m [ Title: %s, Section: %s, id: %s ] \x1b[0m" % (section.top_title.title, section, section.id)
                for s in section.reference_section.all():
                    section.reference_section.remove(s)
                for s in section.reference_subsection.all():
                    section.reference_subsection.remove(s)
                for s in section.reference_title.all():
                    section.reference_title.remove(s)

                full_text = ""
                for sub in Subsection.objects.filter(section=section):
                    full_text = "%s %s" % (full_text, sub.text)

                #for sa in SectionAdditional.objects.filter(section=section):
                #    full_text = "%s %s" % (full_text, sa.text)

                references = ref.findall(full_text)
                for reference in references:
                    try:
                        obj, type_, sub = target_to_section(reference)
                    except:
                        print format_exc()
                    else:
                        #print obj, type_, sub
                        if type_ == "Section":
                            section.reference_section.add(obj)
                            #print "Added reference from %s to section - %s" % (section, obj)
                        if sub:
                            try:
                                subsection = Subsection.objects.get(section=obj, subsection=sub)
                            except Subsection.DoesNotExist:
                                print "Subsection -%s of Section %s Title %s does not exists" % (sub, obj.section, obj.top_title.title)
                            except:
                                pass
                            else:
                                section.reference_subsection.add(subsection)
                                #print "Added reference from %s to subsection - %s" % (section, subsection)
                        if type_ == "Title":
                            print "Added reference from %s to title - %s" % (section, obj)
                            section.reference_title.add(obj)
                            
                section.is_processed = True
                section.save()


