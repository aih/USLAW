#-*- coding: utf-8 -*-
"""Move text to textstore model"""

from django.core.management.base import BaseCommand
import laws.models as models

class Command(BaseCommand):
    help = """Fill store."""
    
    
    def handle(self, *args, **options):
        cll = dir(models)
        for cl in cll:
            model = getattr(models, cl)
            try:
                ts = model.store
            except:
                pass
            else:
                try:
                    ch = model._meta.get_field('text')
                except:
                    pass
                else:
                    print "Working on table %s" % model._meta.db_table
                    for i in model.objects.filter(store__isnull=True):
                        if i.store is None:
                            text = i.text
                            try:
                                raw_text = i.raw_text
                            except:
                                raw_text = None
            
                            textstore = models.TextStore(text=text, raw_text=raw_text)
                            textstore.save()
                            i.store = textstore
                            i.save()
                            
