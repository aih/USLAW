# -*- coding: utf-8 -*-
# Uslaw comments models

from datetime import datetime
from smtplib import SMTPException

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django import forms
from django.db.models.signals import post_save
from django.template import Context, Template
from django.core.mail import send_mail, EmailMessage

from djangosphinx.models import SphinxSearch
from utils.utils import humanizeTimeDiff
from uslaw.users.models import Profile, EmailTemplate

from local_settings import from_email, SITE_URL, MEDIA_URL

class Comment(models.Model):
    """Comments model.
    We can attach comment to any model/object"""
    search = SphinxSearch() # optional: defaults to db_table
    # If your index name does not match MyModel._meta.db_table
    # Note: You can only generate automatic configurations from the ./manage.py script
    # if your index name matches.
    search = SphinxSearch('comment')
    profile = models.ForeignKey(Profile)
    parent = models.ForeignKey('self', null=True, blank=True, default=None)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    rate = models.IntegerField(default=0)
    text = models.TextField(max_length=2000)
    publication_date = models.DateTimeField(default=datetime.now())

    def __unicode__(self):
        return "%s: %s" % (self.profile, self.text[:150])

    def get_absolute_url(self):
        try:
            url = self.content_object.get_absolute_url()+'#'+str(self.id)
        except AttributeError:
            url = ""
        return url
    
    def human_date(self):
        """return humanized date =)  """
        return humanizeTimeDiff(self.publication_date)

    def delete_old_comments(self):
        print "============= Deleting comments without object ======="
        for c in Comment.objects.all():
            if c.content_object is None:
                print "Not exists: %s %s"%(c.content_object, c.object_id)
                c.delete()

    def get_ext_date(self):
        """Return external publication date"""
        return self.publication_date

    def get_name(self):
        return self._meta.verbose_name_plural

    class Meta:
        ordering = ["publication_date"]
        verbose_name_plural = "Comments"    


class Vote(models.Model):
    profile = models.ForeignKey(Profile)
    comment = models.ForeignKey(Comment)
    mark = models.IntegerField(default=0)

    def __unicode__(self):
        return str(self.profile)+" "+str(self.mark)
    
class FollowObject(models.Model):
    """Allow user follow updates for post/question/ any object"""

    profile = models.ForeignKey(Profile)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    publication_date = models.DateTimeField(default=datetime.now())

    def __unicode__(self):
        return unicode(self.profile)


class CommentForm(forms.ModelForm):
    """Comments form"""
    profile = forms.ModelChoiceField(required=False, widget=forms.HiddenInput, queryset=Profile.objects.filter())#forms.IntegerField(widget=forms.HiddenInput(), required=False)
    parent = forms.IntegerField(widget=forms.HiddenInput(), required=False)
#    content_object   = forms.IntegerField(widget=forms.HiddenInput())
    object_id = forms.IntegerField(widget=forms.HiddenInput())
    content_type = forms.ModelChoiceField(widget=forms.HiddenInput, queryset=ContentType.objects.filter()) #forms.IntegerField(widget=forms.HiddenInput())
    text = forms.CharField(widget=forms.Textarea(attrs={"rows":"3", "cols":"40", "class":"comment_text_area",}))
    next = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Comment
        exclude = ('publication_date', 'rate', 'profile',)

class FollowForm(forms.ModelForm):
    """Follow form"""
    object_id = forms.IntegerField(widget=forms.HiddenInput())
    content_type = forms.ModelChoiceField(widget=forms.HiddenInput, queryset=ContentType.objects.filter()) #forms.IntegerField(widget=forms.HiddenInput())
    
    class Meta:
        model = Comment
        exclude = ('publication_date', 'profile',)


#signals

# TODO: move that signal to crontab script ?
def follow_handler(sender, instance, **kwargs):
    """This signal used to send update emails"""
    followers = FollowObject.objects.filter(content_type=instance.content_type, object_id = instance.object_id)
    for f in followers:
        email_template, created = EmailTemplate.objects.get_or_create(name="follow_updates")
        if created:
            email_template.subject = "Tax26.com updates"
            email_template.template= "<html><body>New updates on {{ site_url }}, \r\n click here to see: {{ URL }}</body></html>"#
            email_template.save()
        et = email_template
        site_url = SITE_URL
        t = Template(et.template)
        c = Context(locals())
        message =  t.render(c)
        msg = EmailMessage(et.subject, message, from_email, (f.profile.user.email,))
        msg.content_subtype = "html"
        msg.send()

    return instance

post_save.connect(follow_handler, sender=Comment, dispatch_uid="comment_save_uid")
