#Python
# -*- coding: utf-8 -*-
# Load db with XML of Public Laws (from the enrolled bills)
# 
from django.db import models
from codeupdate.models import *
from laws.models import *

def uniq(inlist):
    # order preserving
    uniques = []
    for item in inlist:
        if item not in uniques:
            uniques.append(item)
    return uniques

def loadpl():
    # Make a dictionary with the Public Law as key and the Bill number as value
    with open('/Users/tabulaw/Documents/workspace/uslaw/codeupdate/data/PLtoHRlist') as plhr:
        plhrdict = dict([each_line.strip().split(' ; ') for each_line in plhr])

    # Get list of new Public Laws that affect 26 USC
    with open('/Users/tabulaw/Documents/workspace/uslaw/codeupdate/data/Classtables_PL', 'r') as publaws:
        publaws_list = [each_line.strip() for each_line in publaws]

    # Load the PL XML (by bill number) to the db
    for publaw in publaws_list:
        (congress,plnum) = publaw.strip().split('-')
        billnum = plhrdict[publaw]
        #open the xml file
        try:
            with open('/Users/tabulaw/Documents/workspace/uslaw/codeupdate/data/newlawsxml/'+congress+'/'+billnum+'_enr.xml','r') as billtext:
                text = billtext.read()
        except IOError:
                print billnum+"_enr.xml Does Not Exist"
                text = None
        newPL = PubLaw(congress=congress, plnum=plnum,billnum=billnum, text=text)
        newPL.save()
