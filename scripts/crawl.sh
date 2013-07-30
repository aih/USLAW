#!/bin/sh
dir=$(dirname $(which $0));
cd $dir
cd ..
source ../../ve/bin/activate
python crawl.py


