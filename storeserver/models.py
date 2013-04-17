# -*- coding: utf-8 -*-
# Models for temporary page storage
# 

from datetime import datetime
import base64

from django.db import models
from django.contrib import admin



class Store(models.Model): 
    """
    Model for links/page storage.
    This table must be cleared from old entries every 2-x days.
    """
    url = models.CharField(max_length=250)
    plugin_id = models.IntegerField(default=0)
    plugin_level = models.IntegerField(default=0)
    category_id = models.IntegerField(default=0)
    page = models.TextField(max_length=100000)
    page_type = models.IntegerField(default=0) # 0 - text, 1 - image, images loaded by special bots (image-bots)
    image_file = models.ImageField(upload_to="tmpimages/%Y/%m/%d", max_length=300, blank=True, null=True)
    status = models.IntegerField(default=0) # 0  - new, 1 - processed, 2 - fail
    error_text = models.CharField(max_length=250, blank=True, null=True) 
    publication_date = models.DateTimeField(default=datetime.now())
    
    
    def __unicode__(self):
        return self.url

    def save(self, *args, **kwargs):
        if self.url[-4:] == ".pdf":
            self.page = ""
        super(Store, self).save(*args, **kwargs)    


    class Meta:
        ordering = ["url"]
  
class Link(models.Model): 
    """
    Model for links which must be downloaded by bots

    This table must be cleared from old entries with status = 1 every day?.
    maybe it's better to
    
    """
   
    url = models.CharField(max_length=250)
    plugin_id = models.IntegerField(default=0)
    plugin_level = models.IntegerField(default=0)
    category_id = models.IntegerField(default=0)    
    decode_charset = models.CharField(default="", max_length=50)
    url_type = models.IntegerField(default=0) # 0 - text, 1 - image, images loaded by special bots (image-bots)
    publication_date = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0) # 0  - New, 1 - Taked by bot
    date_taken = models.DateTimeField(default=datetime.now())
   
    def __unicode__(self):
        return self.url
  
    class Meta:
        ordering = ["url"]
 
       
#class Loaded(models.Model): 
#    """
#    Model for loaded which used to cache loaded links
#    """
    
#    url_hash = models.CharField(unique=True, max_length=500) # Realy this is just url for now
#    plugin_id = models.IntegerField(default=0)
#    publication_date = models.DateTimeField(default=datetime.now())
#    status = models.IntegerField(default=0) # 0  - Ok, 1 - Error
#    
#    def __unicode__(self):
#        return self.url_hash
#  
#    class Meta:
#        ordering = ["-publication_date"]
#        verbose_name_plural = "Loaded"        

        


