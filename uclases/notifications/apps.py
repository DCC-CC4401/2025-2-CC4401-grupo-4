from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    def ready(self):
        """
        Importa los signals y estrategias cuando la app esté lista.
        Esto asegura que los receivers y estrategias se registren automáticamente.
        """
        import notifications.signals  # noqa: F401
        import notifications.strategy.concretestrategies  # noqa: F401
