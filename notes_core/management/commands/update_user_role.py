from django.core.management.base import BaseCommand
from notes_core.models import User

class Command(BaseCommand):
    help = 'Updates user role to ADMINISTRATOR'

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username='admin')
            user.role = User.Role.ADMINISTRATOR
            user.save()
            self.stdout.write(self.style.SUCCESS('Successfully updated user role'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User not found')) 