from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
    
    def ready(self):
        """
        Connect signal handlers or perform other initialization
        """
        # Import any signal handlers if needed
        # No signals defined yet but may be added in the future
        pass