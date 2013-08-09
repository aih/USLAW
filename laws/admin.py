from django.contrib import admin
from laws.models import *

class TitleAdmin(admin.ModelAdmin):
    #list_filter = ["title"]
    search_fields = ['title']
    list_display = [ "name", "title","parent"]

class SubsectionAdmin(admin.ModelAdmin):
    list_display = ['section', 'subsection', ]

class SectionAdmin(admin.ModelAdmin):
    list_display = ['section', 'top_title', "header"]
    list_filter = ["is_active", "is_processed", "top_title",  ]
    search_fields = ["section", ]
    fields = ('title', 'top_title', 'header', 'is_active', 'is_outdated', 
              'url', 'section_text', 'last_update', 'current_through', 'source' )

class SectionAdditionalAdmin(admin.ModelAdmin):
    search_fields = ["section", "text"]

class InternalRevenueManualTocAdmin(admin.ModelAdmin):
    list_display = ["toc", "name", "level", "source_link"]
    search_fields = ["name", "toc"]
    list_filter = ["level"]

class InternalRevenueBulletinTocAdmin(admin.ModelAdmin):
    list_display = ["toc", "name", "level", "source_link"]
    search_fields = ["name", "toc"]
    list_filter = ["level"]


class RegulationAdmin(admin.ModelAdmin):
    list_display = ["section", "title", "rate", ]
    list_filter = ["is_active", "is_outdated", ]
    search_fields = ["text", "title", ]
    fields = ("section", "title", "document", "text", 
              "link", "rate", "is_active", "is_outdated", 
              "external_publication_date", "last_update")

class IRSRevenueRulingsAdmin(admin.ModelAdmin):
    list_display = ["section", "title", "rate", ]
    list_filter = ["is_active", "is_outdated", ]
    search_fields = ["text", "title", ]
    fields = ("section", "title", "document", "text", 
              "link", "rate", "is_active", "is_outdated", 
              "external_publication_date", "last_update")

class IRSPrivateLetterAdmin(admin.ModelAdmin):
    list_display = ["title", "letter_date", "rate", ]
    list_filter = ["is_active", "is_outdated", ]
    search_fields = ["text", "title", ]
    fields = ("section", "title", "document", "text", 
              "link", "rate", "is_active", "is_outdated", 
              "external_publication_date", "last_update")


class PubLawAdmin(admin.ModelAdmin):
    list_display = ["billnum", "plnum", "congress"]

class ClassificationAdmin(admin.ModelAdmin):
    list_display = ["pl", "section"]

class UscodeHtmlAdmin(admin.ModelAdmin):
    list_display = ["url", "publication_date"]

class USCTopicAdmin(admin.ModelAdmin):
    list_display = ["name", "first_section", "last_section"]

class FormAndInstructionAdmin(admin.ModelAdmin):
    list_display = ["product_number", "title", "external_publication_date", ]
    list_filter = ["is_active", "is_outdated", ]
    search_fields = ["text", "title", ]
    fields = ("product_number", "title", "document", "text", 
              "link", "rate", "is_active", "is_outdated", 
              "external_publication_date", "last_update")

class NamedStatuteAdmin(admin.ModelAdmin):
    search_fields = ["title", "description"]
    list_display = ["title", "description"]

class PublicationAdmin(admin.ModelAdmin):
    list_display = ["product_number", "title", "external_publication_date", ]
    list_filter = ["is_active", "is_outdated", ]
    search_fields = ["text", "title", ]
    fields = ("product_number", "title", "document", 
              "link", "rate", "is_active", "is_outdated", 
              "external_publication_date", "last_update")

class DecisionAdmin(admin.ModelAdmin):
    list_display = ["product_number", "title", "description", 
                    "external_publication_date", ]
    list_filter = ["is_active", "is_outdated", ]
    search_fields = ["text", "title", ]
    fields = ("product_number", "title", "description", "document", "text", 
              "link", "rate", "is_active", "is_outdated", 
              "external_publication_date", "last_update")

class InformationLetterAdmin(admin.ModelAdmin):
    list_display = ["product_number", "title", "uilc", 
                    "external_publication_date", ]
    list_filter = ["is_active", "is_outdated", ]
    search_fields = ["text", "title", ]
    fields = ("product_number", "title", "document", "text", "uilc", 
              "link", "rate", "is_active", "is_outdated", 
              "external_publication_date", "last_update")

class WrittenDeterminationAdmin(admin.ModelAdmin):
    list_display = ["product_number", "title", "uilc", 
                    "external_publication_date", ]
    list_filter = ["is_active", "is_outdated", ]
    search_fields = ["title", ]
    fields = ("product_number", "title", "document", "uilc", 
              "link", "rate", "is_active", "is_outdated", 
              "external_publication_date", "last_update")

admin.site.register(Title, TitleAdmin)
admin.site.register(Subsection, SubsectionAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Regulation, RegulationAdmin)
admin.site.register(IRSRevenueRulings, IRSRevenueRulingsAdmin)
admin.site.register(IRSPrivateLetter, IRSPrivateLetterAdmin)

admin.site.register(PubLaw, PubLawAdmin)
admin.site.register(Classification, ClassificationAdmin)
admin.site.register(UscodeHtml, UscodeHtmlAdmin)
admin.site.register(USCTopic, USCTopicAdmin)
admin.site.register(SectionAdditional, SectionAdditionalAdmin)
admin.site.register(FormAndInstruction, FormAndInstructionAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(NamedStatute, NamedStatuteAdmin)
admin.site.register(Decision, DecisionAdmin)
admin.site.register(InformationLetter, InformationLetterAdmin)
admin.site.register(WrittenDetermination, WrittenDeterminationAdmin)
admin.site.register(InternalRevenueManualToc, InternalRevenueManualTocAdmin)
admin.site.register(InternalRevenueBulletinToc, InternalRevenueBulletinTocAdmin)
