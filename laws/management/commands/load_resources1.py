# -*- coding: utf-8 -*-
# wget http://www.access.gpo.gov/nara/cfr/waisidx_09/26cfr1a_09.html --mirror  -D edocket.access.gpo.gov,access.gpo.gov,www.access.gpo.gov -H -np -R pdf,PDF
# wget http://www.access.gpo.gov/nara/cfr/waisidx_09/26cfr1g_09.html --mirror  -D edocket.access.gpo.gov,access.gpo.gov,www.access.gpo.gov -H -np -R pdf,PDF
# wget http://www.access.gpo.gov/nara/cfr/waisidx_09/26cfr1k_09.html --mirror  -D edocket.access.gpo.gov,access.gpo.gov,www.access.gpo.gov -H -np -R pdf,PDF


from __future__ import with_statement
try:
    import re2 as re
except:
    import re
import os, shutil
from django.core.management.base import BaseCommand

from laws.models import *


class Command(BaseCommand):
    help = """Import the Regulations from html format."""

    def handle(self, *args, **options):
        if len(args) == 0:
            print "Please supply the directory of source HTML files as the first argument."
            return

        dirname = args[0]
        sect_re = re.compile(r'Sec\. 1\.(.*?)-(.*?) (.*?)\.', re.DOTALL)
        title = Title.objects.get(title='26')
        repl_re = re.compile(r'\[Page \d+\]')
        good = 0
        bad = 0 
        for root, dirs, files in os.walk(dirname):
            for filename in files:
                path = os.path.join(root, filename)
                with open(path) as f:
                    data = f.read()
                    s = sect_re.findall(data)
                    if len(s)>0:
                        sections = s[0][0].split('(')
                        shutil.copyfile(path, 'site_media/uploads/'+filename)
                        try:
                            section_id = int(sections[0])
                        except ValueError:
                            pass
                        else:
                            try:
                                good = good + 1
                                sec = Section.objects.get(title=title, section=section_id)
                            except Section.DoesNotExist:
                                sec = None
                        
                        if len(sections)==1:
                            section= "1."+s[0][0].strip().replace(".","")+"-"+s[0][1].strip().replace(".","")
                            if len(section)>20:
                                sys.exit("big1")
                            if len(section)>20:
#                                    print title
                                print data
                                #sys.exit("big2")
                            else:
                                data_re = re.compile(r'<BODY(.*?)>(.*?)</BODY>', re.DOTALL)
                                text = data_re.findall(data)
                                #print data
                                #print text
                                a = Regulation(section=section, title=s[0][2][:200], document="uploads/"+filename,  text=text[0][1])
                                a.save()
                                if sec:
                                    a.sections.add(sec)
                            #print "section:", s[0][0],s[0][1]
                        else:
                            
                            #for ss in s:
                            if 1==1:
                                ss=s[0]
                                #print ss
                                section = "1."+ss[0].strip().replace(".","")+"-"+ss[1].strip().replace(".","")
                                title_string = ss[2][:200]

                                #print "section:[%s]" %section
                                #print "``````````````````````````````````"
                                if len(section)>20:
                                    pass
                                    #sys.exit("big2")
                                else:
                                    try:

                                        a = Regulation.objects.get(section=section)
                                    except Regulation.DoesNotExist:
                                        a = Regulation(section=section, title=title_string, document="uploads/"+filename,  text=data)
                                        a.save()
                                        if sec:
                                            a.sections.add(sec)
                                    else:
                                        #print "not unique", section
                                        bad +=1
                                        #sys.exit("Not unique")
                                        pass
                                    

                    if len(s)==0:
                        print "Skipping: ", path
        print good
        print bad
