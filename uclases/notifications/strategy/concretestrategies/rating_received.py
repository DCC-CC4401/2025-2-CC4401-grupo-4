from notifications.strategy.trait import NotificationStrategy
from notifications.strategy.factory import NotificationStrategyFactory
from notifications.enums import NotificationTypes
from django.urls import reverse

@NotificationStrategyFactory.register(NotificationTypes.RATING_RECEIVED)
class RatingReceivedStrategy(NotificationStrategy):
    """Estrategia para notificar al profesor cuando recibe una calificación/review."""

    def get_title(self, data):
        return ""

    def get_message(self, data):
        rating = data['calificacion']
        student = rating.calificador.user.get_full_name() or rating.calificador.user.username
        course = rating.inscripcion.horario_ofertado.oferta.ramo.name
        stars = rating.valoracion

        message = f"{student} te ha calificado con {'⭐' * stars} ({stars}/5) en tu clase de {course}"

        # Si hay comentario, agregar preview
        if rating.comentario:
            comment_preview = rating.comentario[:80] + "..." if len(rating.comentario) > 80 else rating.comentario
            message += f": '{comment_preview}'"
        else:
            message += "."
        
        return message

    def get_actions(self, notification):
        rating = notification.related_object
        myself = rating.calificado
        # Boton para ir a perfil a ver ratings
        return []

    def get_icon(self):
        return "⭐"
