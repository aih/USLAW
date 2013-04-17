from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url('^get/$', 'help.views.get_help', name='get_help'),
)
