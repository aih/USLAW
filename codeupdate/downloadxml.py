#Python
#
#
# downloads XML of all Public Laws which modify 26 USC
# This list is compiled from the Classification tables published at
#  http://uscode.house.gov/classification/tbl112cd_1st.htm (2011) 
#  http://uscode.house.gov/classification/tbl111cd_2nd.htm (2010)
#  From these files, I made a document, Classtables_PL listing just the Public Laws that had been changed.

import os, sys, re, subprocess
from subprocess import PIPE, Popen

location = '/Users/tabulaw/Documents/workspace/uslaw/codeupdate/newlawsxml'
lawsupdate = []

# Open Classtables_PL, import the list, split on '-' and place into a list of tuples.
with open('./data/Classtables_PL2','r') as lawsupdate_list:
    [lawsupdate.append(each_line.strip().split('-')) for each_line in lawsupdate_list]

# Make a dictionary with the Public Law as key and the Bill number as value
with open('./data/PLtoHRlist') as plhr:
    plhrdict = dict([each_line.strip().split(' ; ') for each_line in plhr])

for (congress, publaw) in lawsupdate:
        try:
            finalbill = plhrdict[congress+'-'+publaw]
            print "Finalbill = "+finalbill
            url = "http://www.thomas.gov/home/gpoxmlc"+congress+"/"+finalbill+"_enr.xml"
            args = ['wget', '-r', '-nd', '-l', '1', '-p', '-P', location+"/"+congress, url]
            Popen(args, stdout=PIPE)
        except:
            "Failed on bill:"+congress+'-'+publaw
