# -*- coding: utf-8 -*-
# Post news to twitter
import unicodedata

from django.core.management.base import BaseCommand
from django.utils.html import strip_tags
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from posts.models import Post
from utils.twit import post_message
from utils.shorturl import bitly_short

class Command(BaseCommand):
    help = """Post RSS News to Twitter"""

    def handle(self, *args, **options):
        for p in Post.objects.filter(is_twitted=False).order_by("-id")[:3]:
            s_url = bitly_short("%s%s" % (settings.SITE_URL, p.get_absolute_url()))
            title = p.title[:130]
            message = "%s: %s #tax #law" % (title, s_url)
            message = (unicodedata.normalize('NFKD', message).encode('ascii','ignore'))
            message = str(message)
            l = 129
            while len(message) > 140:
                l -= 1
                title = p.title[:l]
                message = "%s: %s #tax #law" % (title, s_url)
                message = str(unicodedata.normalize('NFKD', message).encode('ascii','ignore'))
            post_message(message)
            p.is_twitted = True
            p.save()

