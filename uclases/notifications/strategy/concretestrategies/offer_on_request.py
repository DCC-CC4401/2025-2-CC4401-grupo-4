from notifications.strategy.trait import NotificationStrategy
from notifications.strategy.factory import NotificationStrategyFactory
from notifications.enums import NotificationTypes
from django.urls import reverse

@NotificationStrategyFactory.register(NotificationTypes.OFFER_ON_REQUEST)
class OfferOnRequestStrategy(NotificationStrategy):
    """Estrategia para notificar al dueño de una solicitud cuando alguien comenta ofreciéndose."""

    def get_title(self, data):
        return ""

    def get_message(self, data):
        comment = data['comentario']
        offerer = comment.publicador.user.get_full_name() or comment.publicador.user.username
        request = comment.solicitud_clase
        course = request.ramo.name
        content_preview = comment.contenido[:80] + "..." if len(comment.contenido) > 80 else comment.contenido
        
        return (f"¡{offerer} está interesado en dar clases de {course}! "
                f"Comentó en tu solicitud '{request.titulo}': '{content_preview}'")

    def get_actions(self, notification):
        return []

    def get_icon(self):
        return "🎯"
