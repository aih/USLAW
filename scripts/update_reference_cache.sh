#!/bin/bash
# Extract references from sections text

dir=$(dirname $(which $0));
cd $dir
cd ..
source ../bin/activate
python manage.py extract_reference --update-cache

