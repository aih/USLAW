#-*- coding: utf-8 -*-
# This command used to run all plugins

from datetime import datetime, timedelta
from subprocess import Popen, PIPE
import hashlib, sys
import traceback
from smtplib import SMTPException

from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.template import Template, Context
from django.core.mail import mail_admins
from django.conf import settings

from plugins.models import *
from log.models import addlog

class Command(BaseCommand):
    """
    This command used to run all plugins
    """
    help = """This command used to run all plugins"""

    
    def handle(self, *args, **options):
        # First check for long-running plugins

        n = datetime.now()-timedelta(seconds=settings.PLUGIN_MAX_WORK_TIME)
        oldplugins = Plugin.objects.filter(status=True, runing=1, last_start__lt=n)
        for p in oldplugins:
            print "Plugin running too long: ", p
            try:
                mail_admins('Attention! Looks like plugin hangs.', "Attention! \r\n Plugin %s running too long, more than %s seconds \n " % (p, settings.PLUGIN_MAX_WORK_TIME), fail_silently=False)
            except SMTPException:
                pass

        plugins = Plugin.objects.filter(status=True).order_by("last_start")[:3]
        for plugin in plugins:
            check_str = plugin.plugin_command
            p1 = Popen(["ps", "ax"], stdout=PIPE)
            output = unicode(p1.communicate()[0],  encoding="utf-8")
            if check_str in output:
                print "Plugin is running, skipping..."
            else:
                #print "Running:", plugin
                plugin.runing = 1
                plugin.last_start = datetime.now()
                plugin.save()

                run = plugin.plugin_command.split(" ")
                p1 = Popen(run, stdout=PIPE)
                output = unicode(p1.communicate()[0], errors='ignore')
                if settings.DEBUG:
                    print output
                try:
                    addlog(text = "PLUGIN Output: %s " % output, sender="plugin_runner", level=0, sobject1 = "-", sobject2 = "-")
                except:
                    print traceback.format_exc()
                plugin.runing=0
                plugin.save()
                from django.db import connection
                connection.close()
                sys.exit(0)

        # collect and print some statistics 

