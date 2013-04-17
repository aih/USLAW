#!/usr/bin/env python

import settings
from django.core.management import setup_environ

setup_environ(settings)

from jabberbot import JabberBot, botcmd
import datetime

from laws.models import Title, Section, Subsection

class LawsJabberBot(JabberBot):

    @botcmd
    def search( self, mess, args):
        """Simple search. Use: search <your text here>"""
        qe = Subsection.search.query(args)
        if len(qe) > 0:
            
            result = "Total: %s results\n" % len(qe)
            i = 0 
            for q in qe:
                if i < 10:
                    i += 1
                    result += "%s: Title: %s, Section %s, text: %s\n\n" % \
                        (i, q.section.top_title.title, q.section.header, 
                         q.raw_text)
            return result
        else:
            return "Nothing found"

    @botcmd
    def section( self, mess, args):
        """Display section text
        
        Use: section 26 1
        where 26 - Title and 1 - section
        """
        try:
            title, section = args.split(" ")
        except:
            return "Error" # FIXME
        title = Title.objects.get(title=title, parent=None)
        print title
        section = Section.objects.get(section=section, top_title=title)
        print section
        subs = Subsection.objects.filter(section=section).order_by("part_id")
        print len(subs)
        result = ""
        for s in subs:
            #print s.raw_text
            result += "  "*s.level + s.raw_text + "\n"
        return result

username = 'tax26@jabber.org'
password = 'Nthvbyfnjh'
bot = LawsJabberBot(username, password)
bot.serve_forever()


