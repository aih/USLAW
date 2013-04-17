# -*- coding: utf-8 -*-
# Private Letter Rulings
# These are found here: http://www.irs.gov/pub/irs-wd/
#

from __future__ import with_statement
try:
    import re2 as re
except:
    import re
import os
import shutil
import sys
from subprocess import Popen, PIPE

from django.core.management.base import BaseCommand

from laws.models import IRSPrivateLetter

class Command(BaseCommand):
    help = """Load and parse IRS private letters rulings from PDF's"""

    def handle(self, *args, **options):
        if len(args) == 0:
            print "Please supply the full path to directory of source PDF files as the first argument."
            return

        dirname = args[0]
        i=0
        for root, dirs, files in os.walk(dirname):
            for filename in files:
                path = os.path.join(root, filename)
                if path[-4:] == '.pdf':
                    i = i + 1
                    print "procces %s" %path
                    text_path = path+".txt"
                    p1 = Popen(["pdftotext", "-layout", path, text_path], stdout=PIPE)
                    output = p1.communicate()[0]
                    try:
                        with open(text_path) as f:
                            data = unicode(f.read(), errors='ignore')
                    except IOError:
                        date = ""
                        data = ""
                    else:
                        date_re = re.compile(r'Release Date: (.*?) ') 
                        date = date_re.findall(data)
                        if len(date)>0:
                            date = date[0]
                        else:
                            date = ""

                    number = filename[:-4]
                    shutil.copyfile(path, 'site_media/uploads/'+filename)
                    document="uploads/"+filename

                    pr = IRSPrivateLetter.objects.get_or_create(section=number, title=number)
                    pr.document = document
                    pr.text = data
                    pr.letter_number = number
                    pr.letter_date = date[:50]
                    pr.save()

                        

        print "Total sections loaded: %s"%i
                    
                
