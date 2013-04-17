#!/bin/bash
# Delete old objects from store server and log

dir=$(dirname $(which $0));
cd $dir
cd ..
source ../bin/activate
python manage.py clear_store
python manage.py clear_log

