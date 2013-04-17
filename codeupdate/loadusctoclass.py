#Python
# -*- coding: utf-8 -*-
# Associate 26 USC section with the PL that changes it.
# Only load from Congress 111, since LRC update covers through Congress 110

classlistfile = '/Users/tabulaw/Documents/workspace/uslaw/codeupdate/data/Classtables'

from loadclassdb import getclasslist
from laws.models import *
from codeupdate.models import *

def loadusctoclass():
    classlist = getclasslist(classlistfile)
    for uscsection in classlist:
        print uscsection
        title = int(uscsection[0])
        top_title = Title.objects.get(title=title)
        section = uscsection[1]
        congress, plnum = uscsection[2].split('-')
        pl = PubLaw.objects.get(congress = congress, plnum=plnum.zfill(3))
        plsection = uscsection[3]
        if int(congress) > 111:
            classelement = Classification.objects.get(
                                                        pl = pl,
                                                        plsection = plsection
                                                     )
            try:
                changed_section = Section.objects.get(section=section, top_title=top_title)
                classelement.uscsection.add(changed_section)
                #print classelement
                classelement.save() 
            except:
                "Not able to find "+uscsection[0]+" U.S.C. "+section
                pass
