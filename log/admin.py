# -*- coding: utf-8 -*-
# Log admin

from django.contrib import admin
from log.models import *

class LogAdmin(admin.ModelAdmin):
    list_filter = ["sender", "sobject1", "sobject2", "publication_date", "level"]
    list_display = ["text", "sender" , "publication_date"]
    search_fields = ["text", "sender"]

admin.site.register(Log, LogAdmin)

