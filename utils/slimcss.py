#!/usr/bin/env python
# slim builded css

import sys
from slimmer import css_slimmer

source = sys.argv[1]
f = open(source)
res = css_slimmer(f.read())
f.close()
f = open(source, "w+")
f.write(res)
f.close()
