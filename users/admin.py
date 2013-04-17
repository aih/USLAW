from django.contrib import admin
from users.models import *

class ProfileAdmin(admin.ModelAdmin):
    list_filter     = ["user", ]

class OptionAdmin(admin.ModelAdmin):
    list_display = ["user", "name", "value"]
    list_filter = ["user", "name", ]

class PositionAdmin(admin.ModelAdmin):
    list_filter = ["title", ]

class EducationAdmin(admin.ModelAdmin):
    list_display = ["school_name", "degree", ]

class EmailConfirmAdmin(admin.ModelAdmin):
    list_display = ["user", ]

class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", ]

class TmpTokenAdmin(admin.ModelAdmin):
    list_display = ["token", ]

class SearchAdmin(admin.ModelAdmin):
    list_display = ["user", "text", "publication_date", ]

class RestorePasswordLinkAdmin(admin.ModelAdmin):
    list_display = ["user", "link_hash", ]


class ActivityDictAdmin(admin.ModelAdmin):
    list_display = ["name", "activity_type", ]

class HistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "activity", ]

#class SecretTokenAdmin(admin.ModelAdmin):
#    list_display = ["profile", ]

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Option, OptionAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Education, EducationAdmin)
admin.site.register(EmailConfirm, EmailConfirmAdmin)
admin.site.register(EmailTemplate, EmailTemplateAdmin)
admin.site.register(TmpToken, TmpTokenAdmin)
admin.site.register(Search, SearchAdmin)
admin.site.register(RestorePasswordLink, RestorePasswordLinkAdmin)
admin.site.register(ActivityDict, ActivityDictAdmin)
admin.site.register(History, HistoryAdmin)

#admin.site.register(SecretToken, SecretTokenAdmin)
