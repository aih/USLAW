#!/bin/bash
dir=$(dirname $(which $0));
cd $dir
cd ..
source ../bin/activate
python manage.py post_twit
