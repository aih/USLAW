# -*- coding: utf-8 -*-
import json, sys
from pydot import *
from subprocess import Popen, PIPE

from django.db import connection, transaction
from django.core.management.base import BaseCommand

from laws.models import Section

class Command(BaseCommand):
    help = """Export reference structure of the US code."""

    def handle(self, *args, **options):


        
        cursor = connection.cursor()
        for section in Section.objects.filter(title__title='26'):
            j = 0
            i = 0 
            graph = None
            graph = Dot('"Title 26 Map. Section %s"'%section.section, graph_type='digraph') 
            test_section = section
            print ">>>>>>>>>>>>>>>. Processing %s" %section
            #if str(section.section)!="" and ',' not in str(section.section) and '_' not in  str(section.section):
            if 1==1:
                j = j + 1
                graph.add_node(Node('"'+str(section.id)+'"', label='"'+str(section.section)+ '"', href='%s.svg' % section.section))
                cursor.execute("""select distinct a.id, b.to_section_id, a.section,  a.header
                       from laws_section_reference_section b, laws_section a 
                       where to_section_id=%s and a.id=b.from_section_id;
                       """%section.id)

                back_refs = cursor.fetchall()
                for b in back_refs:
                    #print b[0], b[1]
                    graph.add_node(Node('"'+str(b[0])+'"', label='"'+str(b[2])+'"', href='%s.svg' % str(b[2])))
                    e = Edge('"'+str(b[0])+'"', '"'+str(section.id)+'"')
                    t = graph.get_edge('"'+str(b[0])+'"', '"'+str(section.id)+'"')
                    if len(t)==0:
                        graph.add_edge(e)

                cursor.execute("""
                      select distinct b.id, a.section_id, b.section, b.header
                        from "laws_subsection" a, "laws_section" b, "laws_section_reference_subsection" c
                       where b.id = c.section_id AND
                             c.subsection_id = a.id AND
                             a.section_id=%s;
                       """%section.id)
                back_refs = cursor.fetchall()
                for b in back_refs:
                    #print b[0], b[1]
                    graph.add_node(Node('"'+str(b[0])+'"', label='"'+str(b[2])+'"', href='%s.svg' % str(b[2])))
                    e = Edge('"'+str(b[0])+'"', '"'+str(section.id)+'"')
                    t = graph.get_edge('"'+str(b[0])+'"', '"'+str(section.id)+'"')
                    if len(t)==0:
                        graph.add_edge(e)


                for ref_sec in section.reference_section.all():
                    graph.add_node(Node('"'+str(ref_sec.id)+'"', label='"'+str(ref_sec.section)+'"', href='%s.svg' % str(ref_sec.section)))
                    e = Edge('"'+str(section.id)+'"', '"'+str(ref_sec.id)+'"')
                    t = graph.get_edge('"'+str(section.id)+'"', '"'+str(ref_sec.id)+'"')
                    if len(t)==0:
                        graph.add_edge(e)

                for ref_subsec in section.reference_subsection.all():
                    ref_sec = ref_subsec.section
                    graph.add_node(Node('"'+str(ref_sec.id)+'"', label='"'+str(ref_sec.section)+'"', href='%s.svg' % str(ref_sec.section)))
                    e = Edge('"'+str(section.id)+'"', '"'+str(ref_sec.id)+'"')
                    t = graph.get_edge('"'+str(section.id)+'"', '"'+str(ref_sec.id)+'"')
                    if len(t)==0:
                        graph.add_edge(e)


            print "======================================="
            print "Section %s" %section
            print "total %s edges" %i
            print "total %s nodes" %j
            output_file = "site_media/map/"+str(test_section.section)+"_section.dot"
            graph.write(output_file)
            p1 = Popen(["dot", "-Tsvg", "%s"%output_file, "-Nfontsize=10" "-osite_media/map/%s.svg" %str(test_section.section)], stdout=PIPE)
            output = p1.communicate()[0]
            #print output
            print "->>>"



      
