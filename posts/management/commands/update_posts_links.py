#
#

from django.core.management.base import BaseCommand
from django.utils.html import strip_tags
from django.contrib.contenttypes.models import ContentType

from posts.models import *

class Command(BaseCommand):
    help = """Upgrade post linkx"""

    def handle(self, *args, **options):
        for p in Post.objects.all():
            p.save()
