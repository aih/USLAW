# -*- coding: utf-8 -*-
# Uslaw main Urls file

from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

from laws.views import my404

admin.autodiscover()

handler404 = 'uslaw.laws.views.my404'

urlpatterns = patterns('',
    (r'^storeserver/', include('storeserver.urls')),
    (r'^api/', include('api.urls')),
    (r'^tinymce/', include('tinymce.urls')),
    (r'^laws/', include('laws.urls')),
    (r'^users/', include('users.urls')),
    (r'^posts/', include('posts.urls')),
    (r'^tags/', include('tags.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^comment/', include('comment.urls')),
    (r'^document/', include('document.urls')),
    (r'^help/', include('help.urls')),
    (r'^f/', include('emailfeed.urls')),
    (r'^$', 'users.views.main_index'),
)
if settings.DEBUG: # Serve static files in debug. 
    urlpatterns += patterns('', (r'^site_media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes' : True}), )
