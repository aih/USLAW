#-*- coding: utf-8 -*-
from datetime import timedelta, datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.template import Template, Context

class Command(BaseCommand):
    """
    Update tag count
    """
    help = """Empty storeserver old objects"""
 
    def handle(self, *args, **options):


        cursor = connection.cursor()
        # Data modifying operation - commit required
        # We use raw SQL, because for this simple operation it is 100x faster
        cursor.execute("update tags_tag a set count=(select count(*) from tags_taggeditem b where a.id=b.tag_id);")
        transaction.commit_unless_managed()
        
        time = 0.0
        for q in connection.queries:
            #print q['sql']
            #print q['time']
            #if len(q['sql'])>200:
            #    print q['sql'][:150]
            time += float(q['time'])
        print len(connection.queries)
        print "Total time", time
