# -*- coding: utf-8 -*-
# Help admin

from django.contrib import admin
from help.models import *

class HelpAdmin(admin.ModelAdmin):
    list_display    = ["url", "widget_id", "text", "publication_date"]
    list_filter = ["url",]

class ShownHelpAdmin(admin.ModelAdmin):
    list_display = ['user', 'notice',]


admin.site.register(Help, HelpAdmin)
admin.site.register(ShownHelp, ShownHelpAdmin)

