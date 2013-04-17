# Simple format text as html

try:
    import re2 as re
except:
    import re
import sys

def texttohtml(text):
    result = "<br />\n".join(text.split("\n"))
    space_re = re.compile(r'[ ]{3}')
    result = re.sub(space_re, '&nbsp;&nbsp;&nbsp; ', result)
    return result

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print "Please provide filename as first argument\n "
    else:
        with open(sys.argv[1]) as f:
            print texttohtml(f.read())
