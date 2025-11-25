from notifications.strategy.trait import NotificationStrategy
from notifications.strategy.factory import NotificationStrategyFactory
from notifications.enums import NotificationTypes
from django.urls import reverse

@NotificationStrategyFactory.register(NotificationTypes.NEW_COMMENT)
class NewCommentStrategy(NotificationStrategy):
    """Estrategia para notificar cuando alguien comenta en una publicación (oferta o solicitud)."""

    def get_title(self, data):
        comment = data['comentario']
        if comment.oferta_clase:
            pub_title = comment.oferta_clase.titulo
            owner = comment.oferta_clase.profesor.user or comment.oferta_clase.profesor.user.username
        else:
            pub_title = comment.solicitud_clase.titulo
            owner = comment.solicitud_clase.solicitante.user or comment.solicitud_clase.solicitante.user.username

        commenter = comment.publicador.user or comment.publicador.user.username
        return f"Nuevo comentario de {commenter} en '{pub_title}'"

    def get_message(self, data):
        comment = data['comentario']
        commenter = comment.publicador.user or comment.publicador.user.username
        content_preview = comment.contenido[:80] + "..." if len(comment.contenido) > 80 else comment.contenido
        
        if comment.oferta_clase:
            publication_title = comment.oferta_clase.titulo
            return f"{commenter} comentó en tu oferta '{publication_title}': '{content_preview}'"
        else:
            publication_title = comment.solicitud_clase.titulo
            return f"{commenter} comentó en tu solicitud '{publication_title}': '{content_preview}'"

    def get_actions(self, notification):
        # Usar el related_object (Comentario) almacenado en la Notification
        comment = getattr(notification, 'related_object', None)
        if not comment:
            return []

        if comment.oferta_clase:
            return [
                {
                    "label": "Ver oferta",
                    "url": reverse('courses:oferta_detail', args=[comment.oferta_clase.id]),
                    "method": "GET",
                    "style": "primary"
                },
            {
                'label': 'Ver comentador',
                'url': reverse('accounts:profile_detail', args=[comment.publicador.user.public_uid]),
                'method': 'GET',
                'style': 'info'
            }
            ]
        else:
            return [
                {
                    "label": "Ver solicitud",
                    "url": reverse('courses:solicitud_detail', args=[comment.solicitud_clase.id]),
                    "method": "GET",
                    "style": "primary"
                },
            {
                'label': 'Ver comentador',
                'url': reverse('accounts:profile_detail', args=[comment.publicador.user.public_uid]),
                'method': 'GET',
                'style': 'info'
            }
            ]

    def get_icon(self):
        return "💬"
