# -*- coding: utf-8 -*-
# Tags admin

from django.contrib import admin
from tags.models import *

class TagAdmin(admin.ModelAdmin):
    list_filter     = ["name", "count" ,]

class TaggedItemAdmin(admin.ModelAdmin):
    list_display    = ["tag", "content_object", "publication_date" ,]
    list_filter     = ["tag", "publication_date" ,]

class OutdatedResourceAdmin(admin.ModelAdmin):
    list_display    = ["user", "content_object", "publication_date","count"]
    list_filter     = ["user", "publication_date" ,]
    

admin.site.register(Tag, TagAdmin)
admin.site.register(TaggedItem, TaggedItemAdmin)
admin.site.register(OutdatedResource, OutdatedResourceAdmin)
