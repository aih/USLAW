# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from users.views import *

urlpatterns = patterns('',
    url('^last_search/?$', last_search),
    url('^linkedinlogin/$', linkedinlogin),
    url('^linkedin/?$', linkedin_callback),
    url('^linkedin-connect/?$', linkedin_connect),
    url('^linkedin-update/?$', linkedin_update),
    url('^error/$', error),
    url('^registration/$', reg, name="registration"),
    url('^home/$', home, name="home"),
    url('^password-reset/$', password_reset),
    url('^password-change/$', password_change),
    url('^resend-email/$', resend_email),
    url('^settings/$', profile_settings),
    url('^profile/$', redirect_profile),
    url('^profile/(\d+)/$', profile),
    url('^user_posts/(\d+)/$', user_posts),
#    url('^get-avatar-info/$', get_avatar_info),
    url('^confirm/(\w+)/$', confirm, name="reg_confirm"),
    url('^login/$', do_login, name="login" ),  #'django.contrib.auth.views.login' ),
    (r'^logout/$', 'django.contrib.auth.views.logout', {"next_page":"/"}),  
)
