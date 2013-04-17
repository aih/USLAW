# -*- coding: utf-8 -*-

import sys, pickle
try:
    import re2 as re
except:
    import re
from optparse import make_option

from django.core.management.base import BaseCommand
from django.conf import settings
from django.template.defaultfilters import striptags
from django.contrib.contenttypes.models import ContentType
from django.db import connection, transaction

from tagger import tagger
from laws.models import *
from utils.load_url import load_url
from tags.models import Tag, TaggedItem

class Command(BaseCommand):
    help = """Extract tags from sections"""
    option_list = BaseCommand.option_list + (
        make_option('--clear',
            action='store_true',
            dest='clear',
            default=False,
            help='Clear processed attribute'),
        make_option('--steps',
            dest='steps',
            default=10,
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
            fraction = 200
            sections = Section.objects.filter(is_processed=False).count()
            if sections == 0: #  All processed
                sys.exit(0) #  Finished

            total_steps = sections/fraction + 2
            steps = options['steps']
            print "-" * 70
            print "\x1b[31m Total sections: %s, total steps: %s, steps per run: %s \x1b[0m" % (sections, total_steps, steps)
            print "-" * 70

            ct = ContentType.objects.get_for_model(Section)
            ignore_words = ["section", "title", "chapter", "subsection", "regulation"]
            for step in xrange(0, steps):
                next_step = step + 1
                for s in Section.objects.filter(is_processed=False).order_by("id")[step*fraction:next_step*fraction]:
                    text = " ".join([striptags(sub.raw_text) for sub in Subsection.objects.filter(section=s, raw_text__isnull=False)])
                    weights = pickle.load(open('tagger/data/dict.pkl', 'rb')) # or your own dictionary
                    myreader = tagger.Reader() # or your own reader class
                    mystemmer = tagger.Stemmer() # or your own stemmer class
                    myrater = tagger.Rater(weights) # or your own... (you got the idea)
                    mytagger = tagger.Tagger(myreader, mystemmer, myrater)
                    tags_count = len(text)/500 #  Sections with small amount of text are ignored
                    if tags_count > 20: #  Maximum 20 tags per section
                        tags_count == 20

                    tags = mytagger(text, 10)

                    for t in tags:
                        if t.string not in ignore_words:
                            tag, c = Tag.objects.get_or_create(name=t.string)
                            to, c = TaggedItem.objects.get_or_create(tag=tag, content_type=ct, object_id=s.id)
                    s.is_processed = True
                    s.save()

                sys.exit(1) #  Not all sections processed yet
