# -*- coding: utf-8 -*-
# Admin configuration for plugins
 
from django.contrib import admin

from plugins.models import *

class PluginAdmin(admin.ModelAdmin):
    """
    Class for Plugin Admin  interface
    """    
    list_display = ('name', 'plugin_id', 'plugin_command', 'last_start', 'status', 'error', 'runing', )
    list_filter = ("plugin_id", "status")

class PluginCheckerIntervalAdmin(admin.ModelAdmin):
    """
    Class for class PluginCheckerInterval
    """
    list_display = ("plugin", "interval", )


class UpdateAdmin(admin.ModelAdmin):
    pass
admin.site.register(Plugin, PluginAdmin)
admin.site.register(PluginCheckerInterval, PluginCheckerIntervalAdmin)
admin.site.register(Update, UpdateAdmin)
