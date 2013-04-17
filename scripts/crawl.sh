#!/bin/sh
dir=$(dirname $(which $0));
cd $dir
cd ..
python crawl.py


