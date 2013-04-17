from django.core.management.base import BaseCommand
from django.utils.html import strip_tags

from laws.models import Law
from django.db import transaction

import gc

def queryset_iterator(queryset, chunksize=1000):
    '''
    Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support ordered query sets.
    '''
    pk = 0
    last_pk = queryset.order_by('-pk')[0].pk
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()


class Command(BaseCommand):
    help = """Update search text field and strip tags"""

    #@transaction.commit_manually
    def handle(self, *args, **options):
        for law in Law.objects.filter(index_text=""):
            law.index_text = strip_tags(law.text)
            #transaction.commit()
            law.save()

