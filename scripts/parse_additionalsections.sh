#!/bin/bash
source ../bin/activate
s="python manage.py parse_additional_sections"
$s
while [ $? != 0 ]
do
   $s
done