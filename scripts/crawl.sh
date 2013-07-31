#!/bin/sh
dir=$(dirname $(which $0));
echo $dir
cd $dir
cd ..
source ../../ve/bin/activate
python crawl.py

