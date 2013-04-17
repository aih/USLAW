# -*- coding: utf-8 -*-
"""Uslaw emailfeed models"""
 
from datetime import datetime
import hashlib
import urllib

from djangosphinx.models import SphinxSearch
from django.db import models
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.conf import settings

from utils.utils import humanizeTimeDiff

class EmailFeed(models.Model):
    """Emailfeed, each user have unique email feed 
    attached to user email address"""

    email = models.CharField(max_length=250, unique=True)
    name = models.CharField(max_length=150, unique=True)
    posts_count = models.IntegerField(default=0)
    publication_date = models.DateTimeField(auto_now=True)

    is_banned = models.BooleanField(default=False)
    ban_reason = models.CharField(max_length=512, null=True, blank=True)
    gravatar_url = models.CharField(max_length=512, null=True, blank=True)


    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs) :
        """ Overriding default save method, 
        so we can automatically create names"""
        if self.id is None:
            self.email = self.email.lower().strip()
            m = hashlib.md5()
            m.update(self.email)
            self.gravatar_url = "http://www.gravatar.com/avatar/%s?" % m.hexdigest() #  Build gravatar url
            default = "%s/img/avatar.png" % settings.MEDIA_URL #  Default avatar
            self.gravatar_url += urllib.urlencode({'d':default, 's':'40'})
            name = slugify(self.email.split('@')[0])
            uniq = False
            i = 0
            while not uniq:
                if EmailFeed.objects.filter(name=name).count() == 0:
                    uniq = True
                else:
                    i += 1
                    name = "%s-%s" % (slugify(self.email.split('@')[0]), i)
            self.name = name
        super(EmailFeed, self).save(*args, **kwargs)
        return None
    
    @models.permalink
    def get_absolute_url(self):
        return reverse('feed', kwargs={'feed_name':self.name})

    class Meta:
        ordering = ["name", ]
        verbose_name_plural = "Email Feeds" 


class FeedPost(models.Model):
    """FeedPost: each email message"""

    emailfeed = models.ForeignKey(EmailFeed)
    subject = models.CharField(max_length=512, default='')
    text = models.TextField()
    publication_date = models.DateTimeField(auto_now=True)

    original_email = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.subject

    @models.permalink
    def get_absolute_url(self):
        return reverse('feed_post', kwargs={'post_id':self.pk})

    def human_date(self):
        """return humanized date  """
        return humanizeTimeDiff(self.publication_date)

    class Meta:
        ordering = ["-publication_date", ]
        verbose_name_plural = "Feed Posts" 


