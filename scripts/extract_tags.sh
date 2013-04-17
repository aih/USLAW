#!/bin/bash
dir=$(dirname $(which $0));
cd $dir
cd ..
source ../bin/activate
s="python manage.py extract_tags"
$s
while [ $? != 0 ]
do
   $s
done