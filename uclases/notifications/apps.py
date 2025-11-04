from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    def ready(self):
        """
        Importa los signals cuando la app esté lista.
        Esto asegura que los receivers se registren automáticamente.
        """
        import notifications.signals  # noqa: F401
