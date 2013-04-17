from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url('^view/(\d+)/$', 'posts.views.view', name='post_view'),
    url('^external/(\d+)/$', 'posts.views.external', name='post_external'),
    url('^delete/(\d+)/$', 'posts.views.delete', name='post_delete'),
    url('^edit/(\d+)/$', 'posts.views.edit', name='post_edit'),
    url('^edit/$', 'posts.views.edit', name='post_edit'),
    url('^get-posts/$', 'posts.views.get_posts', name='get_posts'),
    url('^news/$', 'posts.views.news', name='news'),
    url('^vote/(.*?)/$', 'posts.views.vote', name="vote"),

)
