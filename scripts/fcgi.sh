#!/bin/bash
kill -9 `cat tmp/uslaw.pid`
./run.fcgi
sleep 2
chmod 777 tmp/ -R
