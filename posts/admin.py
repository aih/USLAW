# -*- coding: utf-8 -*-
# News admin

from django.contrib import admin
from posts.models import *

class PostAdmin(admin.ModelAdmin):
    list_filter     = ["profile", "publication_date"]
    list_display    = ["title", "profile", "publication_date"]

class PostTypeAdmin(admin.ModelAdmin):
    list_display     = ["name", "publication_date"]

class RssFeedAdmin(admin.ModelAdmin):
    list_display     = ["channel", "frequency", "last_update", "active"]

class ExternalLinkAdmin(admin.ModelAdmin):
    list_display     = ["url", "publication_date", "views"]

 
admin.site.register(Post, PostAdmin)
admin.site.register(PostType, PostTypeAdmin)
admin.site.register(RssFeed, RssFeedAdmin)
admin.site.register(ExternalLink, ExternalLinkAdmin)

