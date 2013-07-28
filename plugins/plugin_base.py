# -*- coding: utf-8 -*-
# Base plugin class

try:
    import re2 as re
except ImportError:
    import re
import sys
import codecs
import traceback
from datetime import datetime
from subprocess import Popen, PIPE

from django.conf import settings

from storeserver.models import Store, Link
from plugins.models import Plugin
from laws.models import Title
from laws.views import target_to_section
from log.models import addlog

class BasePlugin():
    """Base plugin Class"""

    def __init__(self):
        """Empty Init"""
        pass

    def process_page(self):
        """Should be overidden in plugin"""
        pass

    def replace_this_links(self, data):
        """Replace all 'this' links to Title 26"""
        title = Title.objects.get(title='26', parent=None)
        replaces = {"ref-title-this": title.title, }
        for k, v in replaces.iteritems():
            data = data.replace(k, v)
        return data

    def extract_references(self, data, c_obj):
        """Extract references from text and
        add these references to database"""

        ref = re.compile(r'<a href="/laws/target/(.*?)"')
        references = ref.findall(data)
        for s in c_obj.sections.all(): # remove old references
            c_obj.sections.remove(s)

        for reference in references:
            obj, type_, sub = target_to_section(reference)
            if type_ == "Section":
                c_obj.sections.add(obj)
            if type_ == "Subsection":
                c_obj.sections.add(obj.section)
        return None

    def pdftotext(self, full_filename, text_path, data):
        """Extract text from PDF file"""
        f = open(full_filename, mode="wb")
        try:
            f.write(data)
            f.close()
        except (IOError, OSError):
            print "Can't convert file %s to text" % full_filename
            print traceback.format_exc()
        except:
            print "Can't convert file %s to text" % full_filename
            print traceback.format_exc()
            

        p1 = Popen(["pdftotext", "-layout", "-enc", "UTF-8", 
                    full_filename, text_path], stdout=PIPE)
        output = p1.communicate()[0]
        if settings.DEBUG:
            if output != "":
                print "Pdftotext output: [%s]" % output
        data = ""
        with codecs.open(text_path, "r", encoding="utf-8") as f:
            data = f.read()
        return data

    def run(self, start_urls, plugin_id):
        """Run command:
        choose plugin, links and run process page function"""

        plugin = Plugin.objects.get(plugin_id=plugin_id)
        plugin.last_start = datetime.now()
        plugin.save()
        loaded = Store.objects.filter(plugin_id=plugin_id, status=0)[:10]
        loaded_count = len(loaded)
        new_links = []

        for l in loaded:
            try:
                result = self.process_page(l)                    
            except ValueError:
                print sys.exc_info()
                result = False
                er = str(traceback.format_exc())
                er = er + "\r\n Store page id: "+str(l.id)
                plugin.error = er
                plugin.save()
                addlog(text=er, sender=str(plugin_id), level=2)
                l.status = 2
                l.error = er
                l.save()

            if result != False:
                l.status = 1
                l.save()
                for n in result:
                    nl = Link(url=n[0], plugin_id=plugin_id, 
                              plugin_level=n[1], status=0)
                    nl.save()
                    nl.id = None
                new_links.append(result)

        # Now lets check if end with iteration and start from begining
        if len(new_links) == 0 and loaded_count == 0:
            links_count = Link.objects.filter(plugin_id=plugin_id, 
                                              status=0).count()
            if links_count == 0:
                # No urls for processing, add start point
                for s_url in start_urls:
                    l = Link(url=s_url, plugin_id=plugin_id, 
                             plugin_level=0, url_type=0)
                    l.save()


