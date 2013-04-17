from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from users.models import Profile

class LinkedInAuth:
    def authenticate(self, linkedin_profile):
        # Check the linkedin profile and return a User.
        try:
            p = Profile.objects.get(public_profile = linkedin_profile)
        except Profile.DoesNotExist:
            return None
        else:
            return p.user
    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        return user

