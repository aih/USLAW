#!/bin/bash
dir=$(dirname $(which $0));
cd $dir
cd ..
source ../../ve/bin/activate
python manage.py run_plugins
