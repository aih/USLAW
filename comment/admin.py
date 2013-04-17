from django.contrib import admin
from comment.models import *


class CommentAdmin(admin.ModelAdmin):
    list_display=["profile", "text", "publication_date", ]

class FollowObjectAdmin(admin.ModelAdmin):
    list_display     = ["profile", "publication_date"]

admin.site.register(Comment, CommentAdmin)
admin.site.register(FollowObject, FollowObjectAdmin)    
