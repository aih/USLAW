#Python

try:
    import re2 as re
except:
    import re
import autoparser

path = '/Users/tabulaw/Documents/workspace/DJANGO/uslaw/parserefs/data/usc-6-30/' 
uschtml = '2010usc26.htm'
divider="<!-- documentid:"

thistitle = '26'

def splithtml():
    with open(path+uschtml,'r') as uscfile:
        #Split documents between <documentid:> references
        uscfile = uscfile.read()
        uscfiles = uscfile.split(divider)

#    for file in uscfiles[1:]:
#        file = divider+file
#        filename = re.search(r'documentid:.*?\s', file)
#        filename = 'usc'+filename.group(0).lstrip('documentid:').replace('[','~').strip()+'.htm'
#        with open(path+filename,'w') as outputfile:
#            outputfile.write(file)
    return uscfiles

