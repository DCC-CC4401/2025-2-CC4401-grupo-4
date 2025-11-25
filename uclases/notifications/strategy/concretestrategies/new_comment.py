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
        
        if not notification.related_object:
            return []

        comment = notification.related_object

        oferta = getattr(comment, 'oferta_clase', None)
        if oferta:
            offer_id = getattr(oferta, 'pk', None)
            if offer_id:
                return [
                    {
                        'label': 'Ir a oferta',
                        'url': reverse('courses:oferta_detail', args=[offer_id]),
                        'method': 'GET',
                        'style': 'primary'
                    }
                ]

        solicitud = getattr(comment, 'solicitud_clase', None)
        if solicitud:
            solicitud_id = getattr(solicitud, 'pk', None)
            if solicitud_id:
                return [
                    {
                        'label': 'Ir a solicitud',
                        'url': reverse('courses:solicitud_detail', args=[solicitud_id]),
                        'method': 'GET',
                        'style': 'primary'
                    }
                ]

        return []

    def get_icon(self):
        return "💬"
