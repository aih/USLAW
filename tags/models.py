# -*- coding: utf-8 -*-
# Uslaw tags models
# We can add tags to any object (model)

from datetime import datetime

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.template.defaultfilters import slugify
from django import forms
from django.contrib.auth.models import User
from django.core.mail import mail_admins
from django.db.models.signals import post_save
from django.conf import settings


class Tag(models.Model):
    """Tags dictionary
    Count - cached value of total tag used. Not used for now."""

    name = models.CharField(max_length=50, unique=True)
    count = models.IntegerField(default=1)
    is_users_interest = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs) :
        """ Overriding default save method, so we can automatically lower tags."""
        self.name = self.name.lower()
        super(Tag, self).save(*args, **kwargs)
        return None
    
    @models.permalink
    def get_absolute_url(self):
        return ('tags.views.view_tags', [str(self.id)])


    class Meta:
        ordering = ["name", ]
        verbose_name_plural = "Tags"    

class TaggedItem(models.Model):
    """Tagged items"""

    tag = models.ForeignKey(Tag)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    publication_date = models.DateTimeField(default = datetime.now())

    def __unicode__(self):
        return self.tag.name

#    def save(self, tag_name):
#        """
#        Overriding default save method, so we can automatically create tags.
#        """
#        self.tag, c = Tag.objects.get_or_create(name=str(tag_name).lower())
#        super(TaggedItem, self).save()
#        return result
    
    class Meta:
        ordering = ["-publication_date", ]
        verbose_name_plural = "Taged Objects"    

    
class TaggedItemForm(forms.Form):
    tag = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'post_btn_field_small post_btn',}))
    content_type = forms.IntegerField(widget=forms.HiddenInput())
    object_id = forms.IntegerField(widget=forms.HiddenInput())
#    content_object = forms.IntegerField(widget=forms.HiddenInput())
    next = forms.CharField(max_length=100, widget=forms.HiddenInput())


class OutdatedResource(models.Model):
    """Outdated Resources"""

    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    publication_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return unicode(self.content_object)

    def count(self):
        return OutdatedResource.objects.filter(object_id=self.object_id,
                                               content_type=self.content_type).count()
        
            
class OutdatedResourceForm(forms.Form):
    object_id = forms.IntegerField()
    content_type = forms.IntegerField()

#SIGNALS

def outdatedresource_handler(sender, instance, **kwargs):
    """This signal used to send information to admins about outdated resources"""
    text = """
    Attention: 
    User %s (%sadmin/auth/user/%s/) mark resource %s%s as outdated.
    Total %s users mark this resource as outdated.
    View all outdated resources here: %s/admin/tags/outdatedresource/

    http://tax26.com/
    """ % (instance.user.username, settings.SITE_URL, instance.user.id, settings.SITE_URL, instance.content_object.get_absolute_url(), instance.count(), settings.SITE_URL)
    #print text
    #try:
    mail_admins('[TAX26.COM:INFO] Resource marked as outdated',
                text, fail_silently=True)
    #except SMTPException:
        # TODO add debug information
    #    pass
    #except:
        # TODO add debug information
    #    pass
    return instance

post_save.connect(outdatedresource_handler,
                  sender=OutdatedResource,
                  dispatch_uid="outdatedresource_uid")
