# -*- coding: utf-8 -*-
# Creating missing profiles

import hashlib
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from users.models import Profile

class Command(BaseCommand):
    help = """Import the US legal code from Cornel's XML format."""

    def handle(self, *args, **options):
        users = User.objects.all()
        for u in users:
            try:
                p = Profile.objects.get(user=u)                
            except Profile.DoesNotExist:
                m = hashlib.md5()
                m.update(u.email)
                gravatar = "http://www.gravatar.com/avatar/"+m.hexdigest()
                p = Profile(user=u, rate=0, picter=gravatar)
                p.save()                

