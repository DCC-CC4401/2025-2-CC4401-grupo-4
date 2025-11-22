from notifications.strategy.trait import NotificationStrategy
from notifications.strategy.factory import NotificationStrategyFactory
from notifications.enums import NotificationTypes
from django.urls import reverse

@NotificationStrategyFactory.register(NotificationTypes.NEW_COMMENT)
class NewCommentStrategy(NotificationStrategy):
    """Estrategia para notificar cuando alguien comenta en una publicación (oferta o solicitud)."""

    def get_title(self, data):
        return ""

    def get_message(self, data):
        comment = data['comentario']
        commenter = comment.publicador.user.get_full_name() or comment.publicador.user.username
        content_preview = comment.contenido[:80] + "..." if len(comment.contenido) > 80 else comment.contenido
        
        # Determinar si es oferta o solicitud
        if comment.oferta_clase:
            publication_title = comment.oferta_clase.titulo
            return f"{commenter} comentó en tu oferta '{publication_title}': '{content_preview}'"
        else:
            publication_title = comment.solicitud_clase.titulo
            return f"{commenter} comentó en tu solicitud '{publication_title}': '{content_preview}'"

    def get_actions(self, notification):
        return []

    def get_icon(self):
        return "💬"
