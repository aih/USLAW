# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from document.views import *

urlpatterns = patterns('',
    url('^list/$', document_list, name="document_list"),
    url('^save/$', document_save, name="document_save"),
    url('^delete/$', document_delete, name="document_delete"),

)
