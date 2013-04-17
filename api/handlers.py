# Laws API

from piston.handler import BaseHandler
from piston.utils import rc
from api.handlers import *

from laws.models import *

class TitleHandler(BaseHandler):
    """
    Titles Objects.
    """
    allowed_methods = ('GET',)
    model = Title   
    fields = ("id", "title", "name", )

    def read(self, request, title_id=None, top_title_id=None):
        """
       
        URL: /api/title/<title_id>/ - return a single Title object if `title_id` is given,
        URL: /api/title/top/<top_title_id>/ - return list of all Titles which parent top_title_id
        URL: /api/title/ - return list of all top Titles

        """
        base = Title.objects
        
        if title_id:
            try:
                result = base.get(pk=title_id)
            except Title.DoesNotExist:
                return rc.NOT_FOUND
        elif top_title_id:
            result = base.filter(parent_title=top_title_id)
        else:
            result = base.filter(parent__isnull=True) 
        return result

    #@staticmethod
    #def resource_uri():
    #    return ('title_handler', ['id', ])


class SectionListHandler(BaseHandler):
    """
    Sections
    URL: /api/sections/toptitle/<top_title_id>/ - return list of Sections with top_title_id
    """
    allowed_methods = ('GET', )
    model = Section
    fields = ("id", "section", "header", "title__id", "is_outdated", "is_active", "get_absolute_url")

    def read(self, request, top_title_id=None, title_id=None):
        """Return sections list for Selected Title id or Top title id"""
        if top_title_id:
            return Section.objects.filter(top_title__pk=top_title_id)
        else:
            return Section.objects.filter(title__pk=title_id) 
        print "None"

    @staticmethod
    def resource_uri():
        return ('sectionlist_handler', ['id', ])


class SubSectionListHandler(BaseHandler):
    """Subsection objects"""
    allowed_methods = ('GET', )
    model = Subsection
    fields = ("level",  "is_active", "subsection", "is_outdated", "raw_text", "part_id", "get_absolute_url") #"text",?

    def read(self, request, section_id):
        """Return subssections list for Selected section id"""
        return Subsection.objects.filter(section__pk=section_id).order_by("part_id")

    @staticmethod
    def resource_uri():
        return ('subsectionlist_handler', ['section_id', ])


class SectionAdditionalListHandler(BaseHandler):
    """Additional section texts"""
    allowed_methods = ('GET', )
    model = SectionAdditional
    fields = ("raw_text",  "order", "sa_type_u", "get_absolute_url") #"text",?

    def read(self, request, section_id):
        """Return Additional sections text for Selected section id"""
        return SectionAdditional.objects.filter(section__pk=section_id).order_by("order")

    @staticmethod
    def resource_uri():
        return ('sectionadditionallist_handler', ['section_id', ])

