# -*- coding: utf-8 -*-
# IRS Revenue Rulings
# These are found here: http://www.irs.gov/pub/irs-drop/
#

from __future__ import with_statement
import re
import os
import shutil
import sys
from subprocess import Popen, PIPE

from django.core.management.base import BaseCommand

from laws.models import IRSRevenueRulings, Title
from parserefs.autoparser import parse
from laws.views import target_to_section

class Command(BaseCommand):
    help = """Load and parse IRS revenue rulings from PDF's"""

    def handle(self, *args, **options):
        if len(args) == 0:
            print "Please supply the full path to directory of source PDF files as the first argument."
            return
        title = Title.objects.get(title="26") # Only for Title 26
        dirname = args[0]
        ref = re.compile(r'<a href="/laws/target/(.*?)"')
        i = 0
        for root, dirs, files in os.walk(dirname):
            for filename in files:
                path = os.path.join(root, filename)
                if path[-4:] == '.pdf' and filename[:2] == 'rr':
                    i = i + 1
                    print "procces %s" % path
                    text_path = path+".txt"
                    p1 = Popen(["pdftotext", path, text_path], stdout=PIPE)
                    output = p1.communicate()[0]
                    try:
                        with open(text_path) as f:
                            data = unicode(f.read(), errors='ignore')
                    except IOError:
                        date = ""
                        data = ""

                    number = filename[3:-4]
                    shutil.copyfile(path, 'site_media/uploads/'+filename)
                    document="uploads/"+filename

                    data = parse(data)[0]
                    replaces = {"ref-title-this": title.title, }
                    
                    for k, v in replaces.iteritems():
                        data = data.replace(k,v)


                    pr = IRSRevenueRulings(section = number, title=number, document=document, text = data, )
                    pr.save()
                    
                    #print data
                    references = ref.findall(data)
                    for reference in references:
                        try:
                            obj, type_, sub = target_to_section(reference)
                        except:
                            print format_exc()
                        else:
                            if type_ == "Section":
                                print "SEction Added: %s " % obj
                                pr.sections.add(obj)
                        
        print "Total Revenue Rulings loaded: %s" % i
                    
                
