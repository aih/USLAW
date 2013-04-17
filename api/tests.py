"""
Tests for API
"""

from django.core.urlresolvers import reverse
from django.db.models.loading import get_apps
from django.test import TestCase
from django.test.client import Client
from django.conf import settings

from laws.models import Title, Section

class ApiTest(TestCase):
    """"Abstract class for all tests"""
    fixtures = ["fixtures/test_data.json"]
    
    
    def setUp(self):
        """Setup client for tests and load some test data"""
        self.client = Client()

class ApiTests(ApiTest):
    
    def test_title_handler(self):
        print "Test"
        for t in Title.objects.all():
            print t
        section = Section.objects.filter().order_by("?")[0]
        print section

