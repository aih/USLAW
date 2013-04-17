#-*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.db import connection, transaction

class Command(BaseCommand):
    """
    Empty old logs 2 days or more
    """
    help = """Empty old log objects"""
 
    def handle(self, *args, **options):
        """Handle Django command"""

        cursor = connection.cursor()
        # Data modifying operation - commit required
        # We use raw SQL, because for this simple operation it is 100x faster
        cursor.execute("""delete from log_log 
                                where level<2 
                                  and now()-interval '2 days' > publication_date;""")
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
