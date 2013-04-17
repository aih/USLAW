# -*- coding: utf-8 -*-
# Migrate to store
# 


from django.core.management.base import BaseCommand
from django.conf import settings

from laws.models import Section,Title, Publication, TextStore

class Command(BaseCommand):


    def handle(self, *args, **options):
        for r in Publication.objects.filter(store__isnull=True)[:100]:
            if r.store is None:
                ts = TextStore(text=r.text)
                ts.save()
                r.store = ts
                r.save()
