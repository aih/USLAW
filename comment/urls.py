# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from comment.views import *

urlpatterns = patterns('',
    url('^edit-comment/(\d+)/$', edit_comment, name="edit_comment"),
    url('^del-comment/(\d+)/$', del_comment, name="del_comment"),
    url('^add-comment/$', add_comment),
    url('^vote/(.*?)/$', vote),
    url('^follow/$', follow, name="follow_object"),
)
