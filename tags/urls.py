# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from tags.views import *

urlpatterns = patterns('',
    url('^add/$', add),
    url('^view/(\d+)/$',  view_tags, name="view_tags"),
    url('^suggestion/$',  tags_suggestion, name="tags_suggestion"),
    url('^flag_as_outdated/$',  flag_as_outdated),
    url('^cloud/$', tags_cloud, name="tags_cloud"),

)
