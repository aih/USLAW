# -*- coding: utf-8 -*-
import traceback
from smtplib import SMTPException
from datetime import datetime

from django.db.models.signals import pre_save
from django.db import models
from django.core.mail import mail_admins

from log.models import addlog

class Plugin(models.Model):
    """
    Plugin model

    Administrator can add/edit/delete crawl plugins here
    site_name can be any name. It is used to easy find plugin.
    """
    STATUSES = ((0,'Not active'),
                (1,'Active'),)

    RUN_STATUSES = ((0,'Not runing'),
                (1,'Runing'),)
    
    name = models.CharField(max_length=150, verbose_name="Name")
    description = models.TextField(null=True, blank=True)
    plugin_id = models.IntegerField(verbose_name="Unique Plugin ID", unique=True)
    plugin_command = models.CharField(max_length=150, verbose_name="Plugin command to start", unique=True)
    last_start = models.DateTimeField(default=datetime.now())
    date_added = models.DateTimeField(default=datetime.now())
    status = models.IntegerField(choices=STATUSES, verbose_name="Status of plugin")
    runing = models.IntegerField(choices=RUN_STATUSES, verbose_name="Run status of plugin")
    error = models.TextField(blank=True, null=True)
    download_rate = models.IntegerField(verbose_name="Seconds between page downloading.",  null=True, blank=True)

    def __unicode__(self):
        return str(self.plugin_id)+"=>"+self.name

    class Meta:
        ordering = ["name",]
        verbose_name_plural = "Plugins"      


class Update(models.Model):
    """
    Model for store information about new resources.
    """
    plugin = models.ForeignKey(Plugin)
    update_date = models.DateTimeField(default=datetime.now())
    update_text = models.TextField()

    def __unicode__(self):
        return "%s - %s" % (self.plugin, self.update_text)

class PluginCheckerInterval(models.Model):
    """
    Table for storing plugins check intervals
    """

    plugin = models.ForeignKey(Plugin)
    interval = models.IntegerField(verbose_name="Interval in hours")

    def __unicode__(self):
        return self.plugin.site_name

    class Meta:
        ordering = ["plugin",]
        verbose_name_plural = "Plugins Check intervals"  

def plugin_error_notify(sender, instance, **kwargs):
    """
    Send email to ADMINS when plugin fails
    """
    #from django.conf import settings
    
    if instance.error and instance.error != "" and len(instance.error) > 1:
        try:
            #for a in ADMINS:
            mail_admins('Plugin error', instance.error , fail_silently=False) 
        except SMTPException:
            pass
        except:
            print traceback.format_exc()
            addlog("Error sending email", sender="Plugin_error_notify", level=2)
        else:
            instance.error=""
    return instance

pre_save.connect(plugin_error_notify, sender=Plugin, dispatch_uid="plugin_notifier_uid")
