#-*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
#from vse.storeserver.models import Store, Link
from datetime import timedelta, datetime
from django.db import connection, transaction
from django.template import Template, Context

class Command(BaseCommand):
    """
    Empty storeserver old objects 2 days or more
    """
    help = """Empty storeserver old objects"""
 
    def handle(self, *args, **options):


        cursor = connection.cursor()
        # Data modifying operation - commit required
        # We use raw SQL, because for this simple operation it is 100x faster
        cursor.execute("delete from storeserver_store where status=1 and now()-interval '2 days' > publication_date;")
        transaction.commit_unless_managed()
        cursor.execute("delete from storeserver_link where status=1 and now()-interval '2 days'> publication_date;")
        transaction.commit_unless_managed()
        
        #now = datetime.now()
        #old = now-timedelta(days=2)
        #ss = Store.objects.raw("" )# filter(date__lte=old, status__gt=0).delete()
        #ss = Link.objects.raw("delete from storeserver_link where status>0 and now()-interval '2 days'< date;")#filter(date__lte=old, status__gt=0).delete()

        time = 0.0
        for q in connection.queries:
            #print q['sql']
            #print q['time']
            #if len(q['sql'])>200:
            #    print q['sql'][:150]
            time += float(q['time'])
        print len(connection.queries)
        print "Total time", time
