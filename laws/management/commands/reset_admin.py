from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = """Reset Django Admin password to..."""

    #@transaction.commit_manually
    def handle(self, *args, **options):
        from django.contrib.auth.models import User

        #users = User.objects.all()#filter(username="admin")
        #users[0].set_password('uslaw123');
        #users[0].save()
        print "Command disabled"

