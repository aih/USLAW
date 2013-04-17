# -*- coding: utf-8 -*-
# Uslaw Help models

from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

class Help(models.Model):
    """
    Help messages for urls

    This model used to link urls with related HELP texts.
    We can add help text for any page on our site.
    
    """
    url = models.CharField(max_length=250)
    widget_id = models.CharField(max_length=100, default="id_page_help")
    text = models.TextField()
    one_time_notice = models.BooleanField(default=False, verbose_name="Show this notice only once")
    publication_date = models.DateTimeField(default=datetime.now())

    def __unicode__(self):
        return "%s %s"%(self.url, self.text)
  
    class Meta:
        ordering = ["-publication_date", ]
        verbose_name_plural = "Help texts"


class ShownHelp(models.Model):
    """
    We need this model to store notifications showed for user
    """
    notice = models.ForeignKey(Help)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return self.notice.text
  


