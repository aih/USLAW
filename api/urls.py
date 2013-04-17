# -*- coding: utf-8 -*-
# Uslaw main Urls file

from piston.resource import Resource
from piston.doc import documentation_view

from django.conf.urls.defaults import *

from api.handlers import *
from api.views import *

title_handler = Resource(TitleHandler)

sectionlist_handler = Resource(SectionListHandler)

subsectionlist_handler = Resource(SubSectionListHandler)

sectionadditionallist_handler = Resource(SectionAdditionalListHandler)

urlpatterns = patterns('',
    url(r'^title/(?P<title_id>\d+)/', title_handler, name="title_handler"),
    url(r'^title/top/(?P<top_title_id>\d+)/', title_handler, name="top_title_handler"),
    url(r'^title/', title_handler, name="title_handler"),

    url(r'^sections/toptitle/(?P<top_title_id>\d+)/', sectionlist_handler, name="sectionlist_handler"),
    url(r'^sections/title/(?P<title_id>\d+)/', sectionlist_handler, name="sectionlist_handler"),

    url(r'^subsections/section/(?P<section_id>\d+)/', subsectionlist_handler, name="subsectionlist_handler"),

    url(r'^sectionadditional/section/(?P<section_id>\d+)/', sectionadditionallist_handler, name="sectionadditionallist_handler"),

    url(r'^docs/', documentation_view, name="api_docs"),

)
