#!/bin/bash
source ../bin/activate
s="python manage.py parse_subsections"
$s
while [ $? != 0 ]
do
   $s
done