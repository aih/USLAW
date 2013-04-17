# -*- coding: utf-8 -*-
# Emailfeed admin

from django.contrib import admin
from emailfeed.models import EmailFeed, FeedPost

class EmailFeedAdmin(admin.ModelAdmin):
    list_display = ["email", "posts_count"]
    list_filter = ["email", ]


class FeedPostAdmin(admin.ModelAdmin):
    list_display = ["emailfeed", "subject", "publication_date", ]
    

admin.site.register(EmailFeed, EmailFeedAdmin)
admin.site.register(FeedPost, FeedPostAdmin)
