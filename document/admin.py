from django.contrib import admin
from document.models import *


class DocumentAdmin(admin.ModelAdmin):
    list_display=["profile",  ]

admin.site.register(Document, DocumentAdmin)
