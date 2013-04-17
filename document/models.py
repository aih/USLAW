# -*- coding: utf-8 -*-
# Uslaw documents models
# We can add document object to any object (model)

from datetime import datetime

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django import forms

from uslaw.users.models import Profile


class Document(models.Model):
    """Saved documents/items"""

    profile = models.ForeignKey(Profile)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    publication_date = models.DateTimeField(default = datetime.now())

    def __unicode__(self):
        return self.content_object

    class Meta:
        ordering = ["-publication_date", ]
        verbose_name_plural = "Saved documents"    

