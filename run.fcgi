#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import stat
path1 = os.getcwd()
os.chdir("..")
path2 = os.getcwd()
sys.path.insert(0, path1)
sys.path.insert(0, path2)
os.environ['DJANGO_SETTINGS_MODULE'] = "settings"
from django.core.servers.fastcgi import runfastcgi
socket = path1+'/tmp/uslaw.socket'
pid = path1+'/tmp/uslaw.pid'
print "Socket - %s"%socket
runfastcgi(method="prefork", maxrequests=500, protocol="fcgi", maxchildren=12, maxspare=7, socket=socket, pidfile=pid)
os.chmod(socket, stat.S_IROTH)
