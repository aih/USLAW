#!/bin/bash
hg pull -u
read -p "Reload UWSGI (y/n)?"
[[ "$REPLY" == [yY] ]] && sudo /etc/init.d/uwsgi reload

