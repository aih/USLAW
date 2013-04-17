# -*- coding: utf-8 -*-
"""Tests for Emailfeed App."""


from django.core.urlresolvers import reverse
from django.db.models.loading import get_apps
from django.test import TestCase
from django.test.client import Client
from django.conf import settings

from emailfeed.models import *


class EmailFeedTests(TestCase):
    """Test class for Laws models"""

    def test_save_feed(self):
        self.feed = EmailFeed(email="serge.ulitin@gmail.com")
        self.feed.save()
        self.assertEquals(self.feed.name, "serge.ulitin")

        response = self.client.get(reverse("feed_name", kwargs={ \
                    'feed_name': self.feed.name,} ))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.feed.name)
        
    def test_save_post(self):
        post = FeedPost(emailfeed=self.feed, text="Some test text", subject="Subject")
        post.save()

        response = self.client.get(reverse("feed_post", kwargs={ \
                    'post_id': post.pk,} ))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, post.text)
        self.assertContains(response, post.subject)
        self.assertContains(response, post.emailfeed.name)

        


