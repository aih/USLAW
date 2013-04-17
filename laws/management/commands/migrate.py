from django.core.management.base import BaseCommand
import sys
from django.core import serializers


def migrate(model, size=500, start=0):
    count = model.objects.using('mysql').count()
    print "%s objects in model %s" % (count, model)
    for i in range(start, count, size):
        print i,
        sys.stdout.flush()
        original_data =  model.objects.using('mysql').all()[i:i+size]
        original_data_json = serializers.serialize("json", original_data)
        new_data = serializers.deserialize("json", original_data_json, 
                                           using='default')
        for n in new_data:
            n.save(using='default')



class Command(BaseCommand):
    help = """Migrate from mysql 2 postgresql"""

    #@transaction.commit_manually
    def handle(self, *args, **options):
        migrate(Law)




