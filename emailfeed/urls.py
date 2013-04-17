from django.conf.urls.defaults import *

from emailfeed.views import *

urlpatterns = patterns('',
    url(r'r/(?P<post_id>\d+)/', feed_post, name="feed_post"),
    url(r'(?P<feed_name>.*?)/', feed, name="feed"),
    url(r'', index, name="feed_index"),
)
