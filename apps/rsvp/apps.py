from django.apps import AppConfig


class RsvpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.rsvp'
    
    def ready(self):
        """
        Connect signal handlers when the app is ready
        """
        # Import signal handlers
        import apps.rsvp.signals