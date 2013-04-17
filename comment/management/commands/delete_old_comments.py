# -*- coding: utf-8 -*-
# Delete comments without objects

from django.core.management.base import BaseCommand

from comment.models import Comment

class Command(BaseCommand):
    help = """Delete old comments"""

    def handle(self, *args, **options):
        c = Comment.objects.all()[0].delete_old_comments()
