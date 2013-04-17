#Python
#
#
# downloads all Public Laws which modify 26 USC
# This list is compiled from the Classification tables published at
#  http://uscode.house.gov/classification/tbl112cd_1st.htm (2011) 
#  http://uscode.house.gov/classification/tbl111cd_2nd.htm (2010)
# Downloads are in text format; 'downloadsxml.py' downloads the xml versions, where available

import os, sys, re, subprocess
from subprocess import PIPE, Popen

location = '/Users/tabulaw/Documents/workspace/uslaw/codeupdate/newlaws'
lawsupdate = []

# Open Classtables_PL, import the list, split on '-' and place into a list of tuples.
with open('./Classtables_PL','r') as lawsupdate_list:
    [lawsupdate.append(each_line.strip().split('-')) for each_line in lawsupdate_list]

# wget "http://www.gpo.gov/fdsys/pkg/PLAW-"+$tuple1+"publ"+$tuple2+"/html/PLAW-"+$tuple1+"publ"+$tuple2+".htm"
    for (congress, publaw) in lawsupdate:
        url = "http://www.gpo.gov/fdsys/pkg/PLAW-"+congress+"publ"+publaw+"/html/PLAW-"+congress+"publ"+publaw+".htm"
        args = ['wget', '-r', '-l', '1', '-p', '-P', location, url]
        Popen(args, stdout=PIPE)
