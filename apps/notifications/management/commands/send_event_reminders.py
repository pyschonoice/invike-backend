from django.core.management.base import BaseCommand
from apps.notifications.tasks import send_event_reminders

class Command(BaseCommand):
    help = 'Send reminders for upcoming events'

    def handle(self, *args, **options):
        """
        Execute the command to send event reminders
        """
        event_count = send_event_reminders()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully sent reminders for {event_count} upcoming events')
        )