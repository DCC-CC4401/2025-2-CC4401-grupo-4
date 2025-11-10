from .trait import NotificationStrategy

class NotificationStrategyFallback(NotificationStrategy):
    """Estrategia de notificación por defecto cuando no se encuentra una específica."""

    def get_title(self, data):
        return "Notificación"

    def get_message(self, data):
        return "Tienes una nueva notificación."

    def get_actions(self, notification):
        return []

    def get_icon(self):
        return "🔔"