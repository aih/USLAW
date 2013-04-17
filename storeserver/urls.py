# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from storeserver.views import index, save, get_urls, stat
urlpatterns = patterns('',
    (r'^$', index),  
    (r'^save', save ),  # Saving page to store server
    (r'^get/(\d+)/(.*)', get_urls ),  # Get urls
    (r'^stat', stat),

)
