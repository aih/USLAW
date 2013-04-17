# -*- coding: utf-8 -*-
# Code Update models
# 
import sys

from django.db import models

from laws.models import *


class PubLaw(models.Model):
    congress = models.CharField(max_length = 3)
    plnum = models.CharField(max_length = 3)
    billnum = models.CharField(max_length = 8) 
    text = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return u"P.L. %s-%s" % (self.congress, self.plnum)

class Classification(models.Model):
    pl = models.ForeignKey(PubLaw)
    plsection = models.CharField(max_length = 20)
    plsectiontext = models.TextField(null = True, blank = True)
    uscsection = models.ManyToManyField(Section)
    uscsubsection = models.ManyToManyField(Subsection, null=True, blank=True)

    def __unicode__(self):
        return u"%s %s" % (self.pl, self.plsection)

