# -*- coding: utf-8 -*-
# Uslaw Project
# 

from django.core.management.base import BaseCommand

from laws.models import Regulation

class Command(BaseCommand):
    help = """Update regulations"""
    sender = "Regulations"

    def handle(self, *args, **options):
        for r in Regulation.objects.all():
            r.save()
