# -*- coding: utf-8 -*-
# Admin configuration for storeserver
#

from django.contrib import admin

from storeserver.models import *

class StoreAdmin(admin.ModelAdmin):
    """
    Class for Store Admin  interface
    """
    list_display = ('url', 'plugin_id', 'status', 'error_text','plugin_level', 'publication_date')
    list_filter = ("plugin_id", "plugin_level", "status", )

class LinkAdmin(admin.ModelAdmin):
    """
    Class for Link Admin  interface
    """
    list_display = ('url', 'plugin_id', 'status', 'plugin_level', 'publication_date')
    list_filter = ("plugin_id", "plugin_level", "status", )

admin.site.register(Store, StoreAdmin)

admin.site.register(Link, LinkAdmin)
#admin.site.register(Loaded)
