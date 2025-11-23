from notifications.strategy.trait import NotificationStrategy
from notifications.strategy.factory import NotificationStrategyFactory
from notifications.enums import NotificationTypes
from django.urls import reverse

@NotificationStrategyFactory.register(NotificationTypes.COMMENT_REPLY)
class CommentReplyStrategy(NotificationStrategy):
    """Estrategia para notificar cuando alguien responde a tu comentario."""

    def get_title(self, data):
        return ""

    def get_message(self, data):
        reply_comment = data['comentario_respuesta']
        replier = reply_comment.publicador.user.get_full_name() or reply_comment.publicador.user.username
        content_preview = reply_comment.contenido[:80] + "..." if len(reply_comment.contenido) > 80 else reply_comment.contenido
        
        # Determinar si es oferta o solicitud
        if reply_comment.oferta_clase:
            publication_title = reply_comment.oferta_clase.titulo
            publication_type = "oferta"
        else:
            publication_title = reply_comment.solicitud_clase.titulo
            publication_type = "solicitud"
        
        return f"{replier} respondió a tu comentario en {publication_type} '{publication_title}': '{content_preview}'"

    def get_actions(self, notification):
        return []

    def get_icon(self):
        return "↩️"
