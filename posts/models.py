# -*- coding: utf-8 -*-
# Uslaw posts models and forms
# 

import re
from datetime import datetime
from tinymce.widgets import TinyMCE
from djangosphinx.models import SphinxSearch

from django.db import models
from django import forms

from utils.utils import humanizeTimeDiff
from users.models import Profile
from tags.models import Tag

class PostType(models.Model):
    """
    Post types dictionary
    """
    name = models.CharField(max_length=100, unique=True)
    publication_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        """Unicode representation of model"""
        return self.name

class ExternalLink(models.Model):
    """Model for store all external links from posts here"""

    url = models.CharField(max_length=1512, unique=True)
    publication_date = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)

    def __unicode__(self):
        return self.url
    
    @models.permalink
    def get_absolute_url(self):
        """View external link"""
        return ('posts.views.external', [self.id])

class Post(models.Model):
    """
    Posts (shares) added by users
    """
    search = SphinxSearch('post')
    profile = models.ForeignKey(Profile)
    title = models.CharField(max_length=250)
    text = models.TextField()
    image = models.ImageField(upload_to="uploads/news/%Y-%m-%d/", 
                              blank=True, null=True)
    reference_link = models.URLField(null=True, blank=True)
    rate = models.IntegerField(default=0)
    post_type = models.ForeignKey(PostType)
    source = models.CharField(max_length=200, null=True, blank=True)
    publication_date = models.DateTimeField(auto_now=True)
    is_twitted = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s" % self.title

    @models.permalink
    def get_absolute_url(self):
        """Post absolute url"""
        return ('posts.views.view', [str(self.id)])

    def human_date(self):
        """return humanized date  """
        return humanizeTimeDiff(self.publication_date)
    
    def save(self, *args, **kwargs):
        if self.id is None:
            text = self.text
            links = re.findall(r"href='(.*?)'", text)
            for l in links:
                if "http://" in l:
                    el, c = ExternalLink.objects.get_or_create(url=l)
                    text = text.replace(l, el.get_absolute_url())
            links = re.findall(r'href="(.*?)"', text)
            for l in links:
                if "http://" in l:
                    el, c = ExternalLink.objects.get_or_create(url=l)
                    text = text.replace(l, el.get_absolute_url())
            self.text = text
            if self.reference_link:
                if "http://" in self.reference_link:
                    el, c = ExternalLink.objects.get_or_create( \
                                                 url=self.reference_link)
                    self.reference_link = el.get_absolute_url()

        super(Post, self).save(*args, **kwargs)

    def get_ext_date(self):
        """Return external publication date"""
        return self.publication_date

    def get_name(self):
        return self._meta.verbose_name_plural
       
    class Meta:
        ordering = ["-publication_date", ]
        verbose_name_plural = "Posts"    

class PostVote(models.Model):
    profile = models.ForeignKey(Profile)
    post = models.ForeignKey(Post)
    mark = models.IntegerField(default=0)

    def __unicode__(self):
        return "%s %s" % (self.profile, self.mark)


class RssFeed(models.Model):

    """ Rss sources """
    profile = models.ForeignKey(Profile)
    channel = models.URLField(verbose_name="RSS channel URL")
    channel_label = models.CharField(max_length=200, null=True, blank=True)
    #tags = models.ManyToManyField(Tag, symmetrical=False, blank=True, null=True)
    active = models.BooleanField(default=True)

    frequency = models.IntegerField(default=30, verbose_name="Frequency in minutes")
    publication_date = models.DateTimeField(auto_now=True)
    site_url = models.CharField(max_length=250, verbose_name="Original site url", null=True, blank=True)
    last_update = models.DateTimeField(default=None, null=True, blank=True)

    def __unicode__(self):
        return self.channel

   
class PostForm(forms.ModelForm):
    """
    Post form 
    """
    profile = forms.ModelChoiceField(widget=forms.HiddenInput, 
                                     queryset=Profile.objects.filter())
    npost_type = forms.CharField(widget=forms.HiddenInput)
    #ModelChoiceField(queryset= PostType.objects.filter(), widget=forms.Select(attrs={"class":"post_btn"}), initial="News")
    title = forms.CharField(widget=forms.TextInput(attrs={"class":"post_btn", "onfocus":"$('#id_title').addClass('bold'); var t=$('#id_title').val(); if (t=='Title:'){$('#id_title').val('');}","onblur":"var q=$('#id_title').val(); \r\n if (q=='') {$('#id_title').val('Title:');}"}), initial="Title:")
    text = forms.CharField(widget=TinyMCE( \
            attrs={'cols': 55, 'rows': 25}))
            #forms.Textarea(attrs={"id":"editor",}))
    reference_link = forms.CharField(required=False, 
                                     widget=forms.TextInput( \
                                     attrs={"class":"post_btn", 
                                            "onfocus":"var rlink=$('#id_reference_link').val(); if (rlink=='Add hyperlink...'){$('#id_reference_link').val('http://');}","onblur":"var q=$('#id_reference_link').val(); \r\n if (  q=='' || q=='http://' ) {$('#id_reference_link').val('Add hyperlink...');}"}), 
                                     initial="Add hyperlink...")
    tags = forms.CharField(required=False, 
                           widget=forms.TextInput(attrs={"class":"post_btn bold"}))

    class Meta:
        model = Post
        exclude = ('publication_date', 'post_type','rate',)


class QuestionForm(forms.ModelForm):
    """
    Question form 
    """
    qprofile = forms.ModelChoiceField(widget=forms.HiddenInput, 
                                      queryset=Profile.objects.filter())
    qpost_type = forms.CharField(widget=forms.HiddenInput)
    qtitle = forms.CharField(widget=forms.TextInput( \
            attrs={"class":"post_btn", "style":"width:620px;"}))
    qtext = forms.CharField(required=False, 
                            widget=TinyMCE(attrs={'cols': 55, 'rows': 25}, 
                                           mce_attrs={'width':730, 'height':160}))
    qtags = forms.CharField(required=False, 
                            widget=forms.TextInput(\
                            attrs={"class":"post_btn bold", "style":"width:620px;"}))

    class Meta:
        model = Post
        exclude = ('publication_date', 'post_type', 
                   'title', 'reference_link', 'text', 'rate', 'profile')

    
