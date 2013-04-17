# -*- coding: utf-8 -*-
# Uslaw user models

import hashlib
from datetime import datetime
from smtplib import SMTPException
from random import randint 

from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.core.signals import request_finished
from django.db.models.signals import pre_save, post_save
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.conf import settings

from tags.models import Tag
from laws.models import Subsection

class Search(models.Model):
    """    User search queries.    """
    user = models.ForeignKey(User)
    text = models.CharField(max_length=255, blank=True, default="")
    publication_date = models.DateTimeField(default=datetime.now())

    def __unicode__(self):
        return self.text

    class Meta:
        ordering = ["-publication_date", ]
        verbose_name_plural = "User search queries"    

    class Admin:
        list_display = ('text', 'user', 'publication_date',)
        list_filter = ('text', 'publication_date',)
        ordering = ('user', 'publication_date', )

    

#class MyLaws(models.Model):
#    """User's sections saved"""
#    user = models.ForeignKey(User)
#    section = models.ForeignKey(Section)

#    def __unicode__(self):
#        return "%s : %s" % (self.user.username, self.section.section)

class Position(models.Model):
    """Loaded from linkedin API:

    title		the job title held at the position, as indicated 
                        by the member
    summary		a summary of the member's position	
    start-date		a structured object with month and year fields
                        indicating when the position began	
    end-date		a structured object with month and year fields
                        indicating when the position ended
                        Blank when the position is current
    is-current	        a "true" or "false" value, depending 
                        on whether it is marked current

    Company_ fields:
    name		the name of the company	
    type		indicates if the company is public or private	
    size		the number of employees at the company	
                        Expressed as a range
    industry		the industry in which the company operates	
                        For example, Computer Software or Defense & Space
    ticker		the stock market name for the company, 
                        if the company type is public	
    """
    title = models.CharField(max_length=2512)
    summary = models.TextField(null=True, blank=True)
    start_date = models.CharField(max_length=20, null=True, blank=True)
    end_date = models.CharField(max_length=20, null=True, blank=True)
    company = models.CharField(max_length=2512, null=True, blank=True)
    company_type = models.CharField(max_length=2512, null=True, blank=True)
    company_size = models.CharField(max_length=2512, null=True, blank=True)
    company_industry = models.CharField(max_length=2512, null=True, blank=True)
    company_ticker = models.CharField(max_length=2512, null=True, blank=True)

    def __unicode__(self):
        return self.title


class Education(models.Model):
    """Educations from linkedin API
    school-name	        education	the name of the school, 
                                        as indicated by the member
    field-of-study	education	the field of study at the school,
                                        as indicated by the member	
    start-date	        education	a structured object a year 
                                        field indicating when 
                                        the education began
    end-date	        education	a structured object with a year 
                                        field indicating when the 
                                        education ended	
                                        Blank when the education is current
    degree	        education	a string describing the degree, 
                                        if any, received at this institution	
    activities	        education	a string describing activities 
                                        the member was involved in while 
                                        a student at this institution	
    notes	        education	a string describing other 
                                        details on the member's studies.	

    """
    school_name = models.CharField(max_length=2512) 
    field_of_study = models.CharField(max_length=250, null=True, blank=True)
    start_date = models.CharField(max_length=50, null=True, blank=True)
    end_date = models.CharField(max_length=50, null=True, blank=True)
    degree = models.CharField(max_length=2512, null=True, blank=True)
    activities = models.CharField(max_length=2512, null=True, blank=True)
    notes = models.CharField(max_length=2512, null=True, blank=True)

    def __unicode__(self):
        return self.school_name
   
    
class Profile (models.Model):
    """User profile. Populated with information from linkedin API."""
    user = models.ForeignKey(User)
    # raw_password = models.CharField(max_length=250) 
    # not used any more TODO: remove this field.

    public_profile = models.CharField(max_length=512)
    linkedin_id = models.CharField(max_length=100, null=True, blank=True)
    picter = models.CharField(max_length=250, null=True, blank=True)
    headline = models.CharField(max_length=2500, null=True, blank=True)
    location = models.CharField(max_length=2500, null=True, blank=True)
    industry = models.CharField(max_length=2500, null=True, blank=True)
    summary = models.CharField(max_length=2500, null=True, blank=True)
    specialties = models.CharField(max_length=2500, null=True, blank=True)
    interests = models.CharField(max_length=2500, null=True, blank=True)
    honors = models.CharField(max_length=2500, null=True, blank=True)
    current_status = models.TextField(null=True, blank=True)
    position = models.ManyToManyField(Position, null=True, blank=True)
    education = models.ManyToManyField(Education, null=True, blank=True)
    email_active = models.BooleanField(default=False)
    rate = models.IntegerField(default=0)

    def __unicode__(self):
        return "%s %s" % (self.user.first_name, self.user.last_name)

    @models.permalink
    def get_absolute_url(self):
        return ('users.views.profile', [str(self.id)])

    @models.permalink
    def get_user_posts_url(self):
        return ('users.views.user_posts', [str(self.id)])

    @models.permalink
    def get_settings_url(self):
        return ('users.views.profile_settings')

    def resend_confirmation(self):
        self.email_active = False
        self.save()

    def avatar(self):
        """return user image or default image"""
        if self.picter and self.picter != '':
            return self.picter
        else:
            return "%simg/avatar.png" % settings.MEDIA_URL
    

class Option(models.Model):
    """User options"""
    user = models.ForeignKey(User)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=250, null=True, blank=True)
    bvalue = models.NullBooleanField(null=True, blank=True)
    publication_date = models.DateTimeField(default=datetime.now())

    def __unicode__(self):
        """Options """
        return self.name

def init_options(user):
    """Set initial options values for user  

    return True if one or more options was created
    """
    o, c = Option.objects.get_or_create(user=user, name='linkedin_connect')
    if c:
        o.bvalue = True
        o.save()
    o, c2 = Option.objects.get_or_create(user=user, name='display_help_bubbles')
    if c2:
        o.bvalue = True
        o.save()
    if c or c2:
        return True
    return False
    

class TmpToken(models.Model):
    """Temporary table used to sign up with linkedin"""
    REQUEST_TYPES = (
        (0, 'Login'),   # User login with LinkedIn
        (1, 'Connect'), # User connect profile with LinkedIN
        (2, 'Update'),  # User update profile information from linkedIn
        )
    token = models.CharField(max_length=100)
    token_secret = models.CharField(max_length=100)
    request_type = models.IntegerField(choices=REQUEST_TYPES, default=0)

    def __unicode__(self):
        return self.token
    
class EmailConfirm(models.Model):
    """Temporary table used to confirm users emails"""
    user = models.ForeignKey(User)
    token = models.CharField(max_length=100, blank=True, null=True, default="")

    def __unicode__(self):
        return self.user.username

    @models.permalink
    def get_absolute_url(self):
        return ('users.views.confirm', [self.token])


class EmailTemplate(models.Model):
    """Email templates.
    Use {{ body }} tag for semantic part.

    # required templates:
      "email_confimation"
    """
    name = models.CharField(max_length=150)
    subject = models.CharField(max_length=150)
    template = models.TextField()

    def __unicode__(self):
        """Unicode method"""
        return self.name
    
class ActivityDict(models.Model):
    """Users activity hostory text objects"""
    activity_type = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=250, unique=True)
    
    def __unicode__(self):
        """Unicode method"""
        return self.name

    class Meta:
        verbose_name_plural = "User activity dictionary"
    
class History(models.Model):
    """User activity history"""
    user = models.ForeignKey(User)
    activity = models.ForeignKey(ActivityDict)
    publication_date = models.DateTimeField(default=datetime.now())

    def __unicode__(self):
        return "%s %s" % (self.user, self.history)
    
    class Meta:
        verbose_name_plural = "User activity"
    
#class CommentForm(forms.Form):
#    text = forms.CharField(widget=forms.Textarea(\
#                  attrs={"rows":"3", "cols":"40",}), required=True)
#    object_id = forms.DecimalField()
#    object_type = forms.CharField(max_length=100)
#    parent = forms.CharField(max_length=10, required=False)
#    next = forms.CharField(max_length=200, required=False)


class RegForm(forms.Form):
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)
    rpassword = forms.CharField(max_length=100, widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=100)
    areaofinterest = forms.ModelMultipleChoiceField(required=False,
                            queryset=Tag.objects.filter(is_users_interest=True),
                            widget=forms.CheckboxSelectMultiple)

    def clean_rpassword(self):
        data = self.cleaned_data['rpassword']
        if self.cleaned_data['password'] != self.cleaned_data['rpassword']:
            raise forms.ValidationError("Passwords don't match")
        return data


class AreaOfInterestForm(forms.Form):
    areaofinterest = forms.ModelMultipleChoiceField(required=False, 
                           queryset=Tag.objects.filter(is_users_interest=True),
                           widget=forms.CheckboxSelectMultiple())


class LoginForm(forms.Form):
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)
    email = forms.EmailField(max_length=100)


class PasswordRestoreForm(forms.Form):
    email = forms.EmailField(max_length=100)


class NewPasswordForm(forms.Form):
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)
    rpassword = forms.CharField(max_length=100, widget=forms.PasswordInput)
    link_hash = forms.CharField(max_length=200, widget=forms.HiddenInput)

    def clean_rpassword(self):
        data = self.cleaned_data['rpassword']
        if self.cleaned_data['password'] != self.cleaned_data['rpassword']:
            raise forms.ValidationError("Passwords don't match")
        return data

class ChangePasswordForm(NewPasswordForm):
    oldpassword = forms.CharField(max_length=100, widget=forms.PasswordInput)
    link_hash = forms.CharField(max_length=200, widget=forms.HiddenInput, 
                                required=False)


class RestorePasswordLink(models.Model):
    user = models.ForeignKey(User)
    link_hash = models.CharField(max_length=200)

    def __unicode__(self):
        return str(self.user)
    

class UserSubsection(models.Model):
    profile = models.ForeignKey(Profile)
    subsection = models.ForeignKey(Subsection)

    def __unicode__(self):
        return self.profile

#Some Helpers

def get_user_object(request):
    """Return user object"""
    if request.user.is_authenticated():
        user = request.user
    else:
        try:
            user = User.objects.get(username="Anonymous")
        except User.DoesNotExist:
            user = False
    return user

def get_profile_object(user):
    """Return users profile if exists """
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = False
    return profile


#SIGNALS

def profile_handler(sender, instance, **kwargs):
    """This signal used to send confirmation email"""
    add_token = "tax26"
    if instance.email_active == False:
        try:
            ec, created = EmailConfirm.objects.get_or_create(user=instance.user)
        except User.DoesNotExist:  # User does not exists, 
                                   # so this is possible fixtures data
            created = False        
        if created:
            m = hashlib.md5()
            ran = str(randint(0, 100000))
            m.update(add_token+instance.user.email)
            m.update(ran)
            ec.token = m.hexdigest()
            ec.save()
            email_template, created = EmailTemplate.objects.get_or_create(\
                                                    name="email_confimation")
            if created:
                email_template.subject = "Tax26.com registration confirmation"
                email_template.template = """To confirm your account at %s 
please click the following link: {{ body }}\n\r 
Thank you, \r\n %s""" % (settings.SITE_URL, settings.SITE_URL)
                email_template.save()

            et = email_template
            try:
                confirm_url = reverse("reg_confirm", args=[ec.token, ])
                msg = et.template.replace("{{ body }}", settings.SITE_URL+confirm_url)
                send_mail(et.subject, msg, settings.from_email, 
                          [instance.user.email, ], fail_silently=False)
            except SMTPException:
                # TODO add debug information
                pass
            except:
                # TODO add debug information
                pass
        return instance


def restore_password_handler(sender, instance, **kwargs):
    """This signal used to send password restore link"""
    email_template, created = EmailTemplate.objects.get_or_create(\
                                             name="password_restore")
    if created:
        email_template.subject = "Tax26.com password restore"
        email_template.template = """To restore your password at %s 
please click the following link: {{ body }}\n\r 
Thank you, \r\n %s""" % (settings.SITE_URL, settings.SITE_URL)
        email_template.save()
    et = email_template
    try:
        send_mail(et.subject, et.template.replace("{{ body }}", 
                              settings.SITE_URL+"users/password-reset/?link_hash=%s" % \
                              instance.link_hash), settings.from_email, 
                              [instance.user.email,], fail_silently=False)
    except SMTPException:
        # TODO add debug information
        pass
    except:
        # TODO add debug information
        pass
    return instance


# Installing some signals
post_save.connect(profile_handler, sender=Profile, 
                  dispatch_uid="profile_save_uid")
post_save.connect(restore_password_handler, 
                  sender=RestorePasswordLink, 
                  dispatch_uid="restore_password_save_uid")
