# -*- coding: utf-8 -*-
# Load and parse US Pub.L 
#  http://uscode.house.gov/classification/tbl112cd_1st.htm

import sys
try:
    import re2 as re
except:
    import re

from django.core.management.base import BaseCommand
from django.conf import settings

from laws.models import *
from utils.load_url import load_url

_CLTABLE_URL = "http://uscode.house.gov/classification/tbl112cd_1st.htm"
_PL_URL = "http://thomas.loc.gov/home/LegislativeData.php?&n=PublicLaws"
_PL_BASE_URL = "http://thomas.loc.gov"
_XML_BASE_URL = "http://thomas.loc.gov/home/gpoxmlc112/"

# TODO: allow to parse given congress # 
# For now parsing only last congress 

class Command(BaseCommand):
    help = """Load and parse Pub.Laws/Bills - updates for US Code"""

    def handle(self, *args, **options):
        print "Start"
        cl_table_html, a,b = load_url(_CLTABLE_URL)
        if cl_table_html==False:
            print "Can't load %"%_CLTABLE_URL
            print a,b
            sys.exit(2)

        table_re = re.compile(r'<FONT face=Courier>(.*?)</font>', re.DOTALL)
        cl_table = table_re.findall(cl_table_html)[0].split("\r")
        cl_list = [] # list of sections->pub.l
        i = 0
        for cl in cl_table:
            i += 1
            if i>5:
                title = cl[0:5].strip()
                section = cl[6:18].strip()
                publ = cl[36:44].strip()
                plsection = cl[45:60].strip()
                if len(title)>0 and len(plsection)>0:
                    v = {"title":title, "section":section, "publ":publ, "plsection":plsection,}
                    cl_list.append(v)
        pl_base,a,b = load_url(_PL_URL) # we go here http://thomas.loc.gov/home/LegislativeData.php?&n=PublicLaws
        if pl_base == False:            # and extract link to list of pub laws
            print "Can't load %"%_PL_URL
            print a,b
            sys.exit(2)
        
        pl_search_url_re = re.compile(r'<h3>Select a Range of Public Laws</h3>[\s\r\n]*<ul>[\s\r\n]*<li><a href="(.*?)"')
        try:
            pl_search_url = pl_search_url_re.findall(pl_base)[0]
        except IndexError:
            print "Can't found link to list of pub laws"
            print pl_base
            sys.exit(2)
        bills_page,a,b = load_url(_PL_BASE_URL+pl_search_url)
        if bills_page == False:
            print "Can't load %"%pl_search_url
            print a,b
            sys.exit(2)
        bills_re = re.compile(r'<b>[\s\r\n]*[\d]+[.]</b>[\s\r\n]*<a href="(.*?)">(.*?)</a>') 
        bills_urls = bills_re.findall(bills_page) # next we extract all urls to bills pages
        for b_url in bills_urls:
            bill_url = _PL_BASE_URL+b_url[0]
            bill_num = b_url[1]
            print "Bill num>", bill_num
            print "Loading %s"%bill_url
            bill, a, b = load_url(bill_url)
            if bill == False:
                print "Can't load %"%bill_url
                print a,b
                sys.exit(2)
            pl_num_re = re.compile(r'Became Public Law No:(.*?)\[')
            pl_num = pl_num_re.findall(bill)[0].strip()
            
            legislation_re = re.compile(r'<a href="(.*?)">Text of Legislation</a>') # now we extract urls to legislations
            legislation_url = _PL_BASE_URL+legislation_re.findall(bill)[0]
            legislation,a,b = load_url(legislation_url)
            if legislation == False:
                print "Can't load %"%legislation_url
                print a,b
                sys.exit(2)
            # next we take link to ENR bill (Enrolled Bill [Final as Passed Both House and Senate])
            enr_re = re.compile(r'ENR\)<a href="(.*?)"')
            print enr_re.findall(legislation)
            try:
                enr_url = _PL_BASE_URL+enr_re.findall(legislation)[0]
            except IndexError:
                print "Can't found ENR bill - %s"%legislation_url
                sys.exit()
            enr,a,b = load_url(enr_url)
            if enr == False:
                print "Can't load %"%enr_url
                print a,b
                sys.exit(2)
                
            # finally we need link to XML version
            xml_re = re.compile(r'Bill PDF</a>[\s\r\n/<>td]*<a href="(.*?)">XML</a>')
            try:
                xml_url = _PL_BASE_URL+xml_re.findall(enr)[0]
            except IndexError:
                print "Can't find xml url here- %s"%enr_url
                print enr
                sys.exit(2)
            print xml_url
            #
            # Now we try to find this Pub law in classification teabl
            for cl in cl_list:
                if pl_num == cl["publ"]: # example dict - {'plsection': '5(e)', 'section': '47115', 'publ': '112-21', 'title': '49'}
                    print cl
                    try:
                        title = Title.objects.get(title=cl["title"])
                    except Title.DoesNotExist:
                        print "Titles %s does not exist "%cl["title"]
                        continue
                    sections = Section.objects.filter(top_title=title, section=cl["section"])
                    if len(sections)==0:
                        print "Sections not found"
                        continue

                    xml,a,b = load_url(xml_url)
                    pub_law,c = PubLaw.objects.get_or_create(congress="112", plnum=pl_num, billnum=bill_num)
                    pub_law.text = xml
                    pub_law.save()
                    for s in sections:
                        classification,c = Classification.objects.get_or_create(pl=pub_law, section=s, plsection = cl["plsection"])
                        


                    
