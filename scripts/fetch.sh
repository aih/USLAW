#!/bin/sh
DIR="var/xml"
if [ -d $DIR ]; then
    cd var/xml
    rm -rf *
    # -nd do not create directory structure
    # -r work recursively
    # -l1 only one level of recursion
    # -A file filter
    # --no-parent do not go to parent directories
    wget -r -l1 -nd --no-parent -A .tgz http://voodoo.law.cornell.edu/uscxml/
    find -name '*.tgz' | xargs -n1 tar -zxf
    echo "Done"
else
    echo "Please create directory $DIR"
fi
