from optparse import make_option

import sys

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from laws.models import Section, Subsection

class Command(BaseCommand):
    help = """Export reference structure of the US code."""
    option_list = BaseCommand.option_list + (
        make_option('--clear',
            action='store_true',
            dest='clear',
            default=False,
            help='Clear processed attribute'),
        make_option('--steps',
            dest='steps',
            default=20,
            help='Count of steps processed per run'),
        )

    def clear(self):
        cursor = connection.cursor()
        # Data modifying operation - commit required
        # We use raw SQL, because for this simple operation it is 100x faster
        cursor.execute("update laws_section set is_processed=False;")
        transaction.commit_unless_managed()
        
    def handle(self, *args, **options):

        if options['clear'] == True: #  Clear processed attribute
            self.clear()
        else:
            fraction = 1000
            subs = Section.objects.filter(is_processed=False).count()
            if subs == 0: #  All processed
                sys.exit(0) #  Finished

            total_steps = subs/fraction + 2
            steps = options['steps']
            print "-" * 70
            print "\x1b[31m Total sections: %s, total steps: %s, steps per run: %s \x1b[0m" % (subs, total_steps, steps)
            print "-" * 70
            for step in xrange(0, steps):
                print "Step %s of %s" % (step, steps)
                next_step = step + 1
                for sec in Section.objects.filter(is_processed=False).order_by("id")[step*fraction:next_step*fraction]:
                    text = " ".join([s.raw_text for s in Subsection.objects.filter(section=sec, text__isnull=False).order_by("part_id")])
                    sec.section_text = text
                    sec.is_processed = True
                    sec.save()
                    
            sys.exit(1) #  Not all sections processed yet
