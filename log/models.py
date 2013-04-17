# Tabulaw log table
from datetime import datetime

from django.db import models
from django.core.mail import mail_admins

LOG_LEVELS = (
    (0, 'Debug'),
    (1, 'Warning'),
    (2, 'Error'),
    )

class Log(models.Model):
    text = models.TextField()
    sender = models.CharField(max_length=100, default="Unknown")
    sobject1 = models.CharField(max_length=300, default="Uknown", verbose_name="Sort object 1") # Sort object1
    sobject2 = models.CharField(max_length=300, default="Uknown", verbose_name="Sort object 2") # Sort object2
    publication_date = models.DateTimeField(default = datetime.now())
    level = models.IntegerField(choices = LOG_LEVELS, default=0)

    def __unicode__(self):
        return self.text[:100]



def addlog(text="", sender="Unknown", level=0, sobject1="Unknown", sobject2="Uknown"):
    l = Log(text=text, sender=unicode(sender[:300]), level=level, sobject1=sobject1[:300], sobject2=sobject2[:100])
    l.save()
    if level == 2:
        mail_admins("ERROR. Sender: %s " % sender, text, fail_silently=True)

        
