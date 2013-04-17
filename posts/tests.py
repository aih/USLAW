# -*- coding: utf-8 -*-
"""Tests for Laws App."""

import os
from urllib import quote

from django.core.urlresolvers import reverse
from django.db.models.loading import get_apps
from django.test import TestCase
from django.test.client import Client
from django.conf import settings
from django.core.paginator import Paginator,InvalidPage, EmptyPage

from posts.models import *
from users.models import Profile

class PostTest(TestCase):
    """"Abstract class for all tests"""
    app_module_paths = []
    for app in get_apps():
        if hasattr(app, '__path__'):
            # It's a 'models/' subpackage
            for path in app.__path__:
                app_module_paths.append(path)
        else:
            # It's a models.py module
            app_module_paths.append(app.__file__)

    fixtures = ["users/fixtures/users.json", "posts/fixtures/posts.json",]
    #app_fixtures = [os.path.join(os.path.dirname(path), \
            #'fixtures') for path in app_module_paths]
    #fixtures = []
    #for app in app_fixtures:
    #    if os.path.exists(app):
    #        fixtures.extend(sorted([i for i in os.listdir(app)]))
     
    
    def setUp(self):
        """Setup client for tests and load some test data"""
        self.client = Client()
        # Add some test data.

class PostModelsTests(PostTest):
    """Test class for Posts models"""
    def test_post_save(self):
        profile = Profile.objects.filter()[0]
        pt = PostType.objects.get(name="News")
        url1 = "http://google.com/?id=123"
        url2 = "http://www.fake.com/?id=321"
        post = Post(title="This is test post", profile=profile,
                    text="""This is Post text 
                    <a href="%s">123</a> also some links
                    <a href='%s'>321</a> also some links""" % (url1, url2),
                    rate=100, post_type=pt)
        post.save()
        self.assertTrue(url1 not in post.text)
        self.assertTrue(url2 not in post.text)
        self.assertEquals(ExternalLink.objects.filter(url=url1).count(), 1)
        self.assertEquals(ExternalLink.objects.filter(url=url2).count(), 1)

class PostViewsTests(PostTest):
    """Test views.py module """

    def test_view(self):
        posts = Post.objects.filter()
        for p in posts:
            response = self.client.get(reverse("post_view", 
                                           args=[p.id]))
            self.assertEquals(response.status_code, 200)
            #self.assertContains(response, p.title )  # FIXME: we have some problems with unicode output...
             
    def test_news(self):
        """Test news view (used for bots)"""
        post_type = PostType.objects.get(name="News")
        posts = Post.objects.filter(post_type=post_type).select_related().order_by("-publication_date")
        p = Paginator(posts, 25)
        try:
            page = p.page(1)
        except (EmptyPage, InvalidPage):
            page = [] #p.page(p.num_pages)

        response = self.client.get(reverse("news"))
        self.assertEquals(response.status_code, 200)
        for p in page.object_list:
            #self.assertContains(response, p.title)   # FIXME: we have some problems with unicode output...
            self.assertContains(response, p.get_absolute_url())

    def test_get_posts(self):
        """Test get_posts view"""
        post_type = PostType.objects.get(name="News")
        posts = Post.objects.filter(post_type=post_type).select_related().order_by("-publication_date")[:4]
        response = self.client.post(reverse("get_posts"), 
                                    data={"page_id":1, "post_type":"News"})
        self.assertEquals(response.status_code, 404)  # Not ajax request

        response = self.client.post(reverse("get_posts"), 
                                    data={"page_id":1, "post_type":"News"}, 
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        for p in posts:
            #self.assertContains(response, p.title)  # FIXME: we have some problems with unicode output...
            self.assertContains(response, p.get_absolute_url())

        post_type = PostType.objects.get(name="Question")
        posts = Post.objects.filter(post_type=post_type).select_related().order_by("-publication_date")[:4]
        response = self.client.post(reverse("get_posts"), 
                                    data={"page_id":1, "post_type":"Question"},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        for p in posts:
            self.assertContains(response, p.title)
            self.assertContains(response, p.get_absolute_url())

    def test_vote(self):
        """Testing vote"""
        post = Post.objects.filter()[0]
        response = self.client.get("%s?post_id=%s" % (reverse("vote", args=["1"]), post.id))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "success")
        self.assertContains(response, "false")

    def test_external(self):
        p = ExternalLink.objects.filter()[0]
        old_views = p.views + 1 
        response = self.client.get(reverse("post_external", args=[p.id]))
        self.assertEquals(response.status_code, 200)
        p2 = ExternalLink.objects.get(pk=p.id)
        self.assertEquals(p2.views, old_views)
        
   
