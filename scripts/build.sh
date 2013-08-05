#!/bin/bash
dir=$(dirname $(which $0));
cd $dir
cd ..
JSDIR="./static/js"
cat $JSDIR/jquery-1.4.4.min.js \
$JSDIR/jquery-ui-1.8.11.custom.min.js \
$JSDIR/jquery.qtip-1.0.0-rc3.min.js \
$JSDIR/main.js > $JSDIR/builded.js

CSSDIR="./static/css"
cat $CSSDIR/newstyle.css \
$CSSDIR/jquery-ui-1.8.11.custom.css > $CSSDIR/builded.css
python utils/slimcss.py $CSSDIR/builded.css



