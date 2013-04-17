#-*- coding: utf-8 -*-
from datetime import timedelta, datetime
import re

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from emailfeed.models import EmailFeed, FeedPost
from utils.emailclient import get_mail

class Command(BaseCommand):
    """
    Load emails to EmailFeed
    """
    help = """    Load emails to EmailFeed"""
 
    def handle(self, *args, **options):
        email_re = re.compile(r"<(.*?)>")
        mails = get_mail(settings.FEED_EMAIL_SERVER, settings.FEED_EMAIL_LOGIN,
                         settings.FEED_EMAIL_PASSWORD)
        for mail in mails:
            print "Processing:", mail['from']
            try:
                email = email_re.findall(mail['from'])[0]
            except IndexError:
                print mail['from']
                email = mail['from']
            feed, c = EmailFeed.objects.get_or_create(email=email)
            msg = unicode(mail['original_msg'], errors='ignore')
            text = unicode(mail['msg'], errors='ignore')
            post, c = FeedPost.objects.get_or_create(emailfeed=feed, 
                                       subject=mail['subject'], 
                                       text=text)
            post.original_msg = msg
            post.save()

            
