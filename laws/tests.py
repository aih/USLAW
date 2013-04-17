# -*- coding: utf-8 -*-
"""Tests for Laws App."""

import os
from urllib import quote

from django.core.urlresolvers import reverse
from django.db.models.loading import get_apps
from django.test import TestCase
from django.test.client import Client
from django.conf import settings
from django.template.defaultfilters import safe, truncatewords

from laws.models import *
from laws.views import target_to_section

from django.core.management import call_command

class LawsTest(TestCase):
    """"Abstract class for all tests"""

    #app_module_paths = []
    #for app in get_apps():
    #    if hasattr(app, '__path__'):
    #        # It's a 'models/' subpackage
    #        for path in app.__path__:
    #            app_module_paths.append(path)
    #    else:
    #        # It's a models.py module
    #        app_module_paths.append(app.__file__)

    #app_fixtures = [os.path.join(os.path.dirname(path), \
            #'fixtures') for path in app_module_paths]
    #fixtures = []
    #for app in app_fixtures:
    #    if os.path.exists(app):
    #        fixtures.extend(sorted([i for i in os.listdir(app)]))
    fixtures = ["fixtures/test_data.json"]
   
    
    def setUp(self):
        """Setup client for tests and load some test data"""
        self.client = Client()

        

class LawsModelsTests(LawsTest):
    """Test class for Laws models"""

    def test_int_to_roman(self):
        #call_command("dumpdata", "laws", indent=2)
        self.assertEquals(int_to_roman(1), 'I')
        self.assertEquals(int_to_roman(2), 'II')
        self.assertEquals(int_to_roman(3), 'III')
        self.assertEquals(int_to_roman(4), 'IV')
        self.assertEquals(int_to_roman(5), 'V')
        self.assertEquals(int_to_roman(15), 'XV')
        self.assertEquals(int_to_roman(25), 'XXV')

    def test_roman_to_int(self):
        self.assertEquals(roman_to_int('I'), 1)
        self.assertEquals(roman_to_int('II'), 2)
        self.assertEquals(roman_to_int('III'), 3)
        self.assertEquals(roman_to_int('IV'), 4)
        self.assertEquals(roman_to_int('V'), 5)
        self.assertEquals(roman_to_int('XV'), 15)
        self.assertEquals(roman_to_int('XXVI'), 26)

    def test_title_save(self):
        t = Title(title="999999", name="Test Title - 999", 
                  text = "Test Title")
        t.save()
        test_title = Title.objects.get(title="999999", parent=None)
        self.assertEquals(test_title.title, "999999")
        self.assertEquals(test_title.name, "Test Title -  999")

        t2 = Title(title="", name="Title 21C - TEST", 
                   text = "Test Title222")
        t2.save()
        test_title2 = Title.objects.get(name="Title 21C - TEST", parent=None)
        self.assertEquals(test_title2.int_title, 45)
        self.assertEquals(test_title2.islast, True)
        test_title2.parent = test_title
        test_title2.save()
        self.assertEquals(test_title.islast, False)

    # Sections
    
    def test_section_view(self):
        section = Section.objects.filter().order_by("?")[0]
        subsections = Subsection.objects.filter(section=section)
        response = self.client.get(reverse("laws_section", kwargs={ \
                    'title':unicode(section.top_title.title), 
                    'section':section.section, 
                    'section_id':section.id}))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, section.section)
        
        for subs in subsections:
            self.assertContains(response, subs.text)
            

    def test_section_save(self):
        title = Title.objects.filter()[0]
        s = Section(title=title, section="1111k", header="Test Header")
        s.save()
        top_title = s.get_title()
        s.top_title = top_title
        s.save()

        response = self.client.get(reverse("laws_section", kwargs={ \
                    'title':unicode(s.title.url), 
                    'section':s.section, 
                    'section_id':s.id}))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, unicode(s.title.title))
        self.assertContains(response, unicode(s.top_title.title))
        self.assertTrue(isinstance(s.get_title(), Title))
        

    # Subsections
    
    def test_subsection_save(self):
        title = Title.objects.filter()[0]
        section = Section.objects.filter(title=title)[0]
        s = Subsection(section=section, text = "Subsection text", 
                       raw_text="Raw text")
        s.save()
        self.assertEquals(s.section, section)
        self.assertEquals(s.text, "Subsection text")
        self.assertEquals(s.raw_text, "Raw text")
        self.assertEquals("%s#%s" % (s.section.get_absolute_url(), s.id), 
                          s.get_absolute_url())
        #self.assertTrue(isinstance(s.get_title(), Title)

class LawsViews(LawsTest):
    """Test views.py module """

    def test_laws_index(self):
        """Test laws_index view"""
        response = self.client.get(reverse("laws_index"))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "TITLE 26")
        self.assertContains(response, "INTERNAL REVENUE CODE")

    def test_title_index(self):
        """Test for title_index view"""
        title = Title.objects.filter(parent=None).order_by("?")[0]
        response = self.client.get(reverse("title_index", kwargs={ \
                    'title_url':title.url, 'title_id':title.id}))
        
        self.assertEquals(response.status_code, 200)

        for sub_title in Title.objects.filter(parent=title):
            #print "Title %s" % sub_title.id
            self.assertContains(response, sub_title.title)

        response = self.client.get(reverse("title_index", kwargs={ \
                    'title_url':'title-7-agriculture', 'title_id':9999999999}))
        self.assertEquals(response.status_code, 404)


    def test_title_text_ajax(self):
        """Test for title_text view """
        title = Title.objects.filter()[0]
        response = self.client.get(reverse("title_text", 
                                           kwargs={'title_id':title.id}))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, unicode(title.text))

    def test_topics(self):
        """Test for laws_topics view"""
        response = self.client.get(reverse("laws_topics"))
        self.assertEquals(response.status_code, 200)
        for t in USCTopic.objects.all():
            self.assertContains(response, unicode(t.name))

    def test_load_topic(self):
        """Test for load_topic view"""
        topic = USCTopic.objects.filter()[0]
        response = self.client.get("%s?pk=%s" % \
                                       (reverse("load_topic"), topic.id))
        self.assertEquals(response.status_code, 200)
        title = Title.objects.get(title='26') #FIXME: Only Title 26 for now. 
        sections = Section.objects.filter( \
            int_section__gte=topic.first_section.int_section, 
            int_section__lte=topic.last_section.int_section, 
            top_title=title)
        for s in sections:
            self.assertContains(response, unicode(s))
            
    def test_section_redirect_map(self):
        """Test for laws_section_redirect_map view
        redirects from TaxMap"""
        section = Section.objects.filter()[0]
        response = self.client.get(reverse("laws_section_redirect_map", 
                                           args=['-', section.id,]))
        self.assertRedirects(response, section.get_absolute_url())

        response = self.client.get(reverse("laws_section_redirect_map", 
                                           args=['-', 999999999,]))
        self.assertEquals(response.status_code, 404)

    def test_section_redirect(self):
        """Test for redirects like /laws/26/1/ """
        section = Section.objects.filter()[0]
        response = self.client.get(reverse("laws_section_redirect", kwargs={ \
                    "title":section.top_title.title, 
                    "section":section.section}))
        self.assertRedirects(response, section.get_absolute_url())

        response = self.client.get(reverse("laws_section_redirect", kwargs={ \
                    "title":section.top_title.title, 
                    "section":'fake'}))
        self.assertEquals(response.status_code, 404)
        
    def test_title_redirect(self):
        """Test for laws_title_redirect"""
        title = Title.objects.filter(parent=None)[0]
        response = self.client.get(reverse("laws_title_redirect", 
                                           kwargs={"title":title.title,}))
        self.assertRedirects(response, title.get_absolute_url())

        response = self.client.get(reverse("laws_title_redirect", 
                                           kwargs={"title":'fake',}))
        self.assertEquals(response.status_code, 404)

    def test_target_to_section(self): 
        """Test for target_to_section function"""
        pass

    def test_print_it(self):
        """Test for print_ir view"""
        section = Section.objects.filter().order_by("?")[0]
        subsections = Subsection.objects.filter(section=section)
        sa = SectionAdditional.objects.filter(section=section)
        response = self.client.get(reverse("print_section", kwargs={ \
                    "section_url": section.url, 
                    "section_id":section.id,
                    "psection":None}))
        self.assertEquals(response.status_code, 200)
        for subs in subsections:
            self.assertContains(response, subs.text)
        for s in sa:
            self.assertContains(response, s.text)

       
    def test_preview_section(self):
        """Test for preview_section view"""
        section = Section.objects.filter(section='1')[0]
        subsection = Subsection.objects.filter(section=section).order_by("part_id")[0]
        response = self.client.get(reverse("preview_section", 
                                           args=[section.id]))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, truncatewords(safe(subsection.text),200))
            
        
    def test_section(self):
        """Test for section view"""
        section = Section.objects.filter().order_by("?")[0]
        subs = Subsection.objects.filter(section=section)
        additional_sections = SectionAdditional.objects.filter(section=section)
        regulations = Regulation.objects.filter(sections=section)
        publaws = Classification.objects.filter(section=section)

        response = self.client.get(reverse("laws_section",  kwargs={ \
                    'title':unicode(section.top_title.title), 
                    'section':section.section, 
                    'section_id':section.id}))
        self.assertEquals(response.status_code, 200)

        for subs in subs:
            self.assertContains(response, subs.text)

        for subs in additional_sections:
            self.assertContains(response, subs.text)

        for r in regulations:
            self.assertContains(response, unicode(r))

        for r in publaws:
            self.assertContains(response, unicode(r.pl))
            self.assertContains(response, unicode(r.section))


    def test_search(self):
        """Test search view. 
        We does not have sphinx for test database
        so we test redirects"""
        section = Section.objects.filter()[0]
        query = "%s usc %s" % (section.top_title.title, section.section)
        url = (reverse("laws_search"))
        response = self.client.get(url, {"page": 1, "where": "everywhere", 
                                         "query": query, })
        self.assertRedirects(response, section.get_absolute_url())
        
    def test_load_regulations(self):
        """Test for load_regulations view"""
        response = self.client.get("%s?section=%s" % \
                                       (reverse("load_regulations"), 'fail'))
        self.assertEquals(response.status_code, 404)

        r = Regulation.objects.filter()[0]
        section = r.main_section
        response = self.client.get("%s?section=%s" % \
                                       (reverse("load_regulations"), section.id))
        self.assertEquals(response.status_code, 200)
        for r in Regulation.objects.filter(main_section=section):
            self.assertContains(response, unicode(r.get_absolute_url()))    

    def test_load_rulings(self):
        """Test for load_rulings view"""
        response = self.client.get("%s?section=%s" % \
                                       (reverse("load_rulings"), 'fail'))
        self.assertEquals(response.status_code, 404)

        irs = IRSRevenueRulings.objects.filter()[0]
        section = irs.sections.all()[0]
        response = self.client.get("%s?section=%s" % \
                                       (reverse("load_rulings"), section.id))
        self.assertEquals(response.status_code, 200)
        for r in IRSRevenueRulings.objects.filter(sections=section):
            self.assertContains(response, unicode(r.get_absolute_url()))    

    def test_goto_section(self):
        response = self.client.get((reverse("goto_section")))
        self.assertEquals(response.status_code, 404)

