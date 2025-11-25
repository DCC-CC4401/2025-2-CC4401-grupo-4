from notifications.strategy.trait import NotificationStrategy
from notifications.strategy.factory import NotificationStrategyFactory
from notifications.enums import NotificationTypes
from django.urls import reverse

@NotificationStrategyFactory.register(NotificationTypes.RATING_RECEIVED)
class RatingReceivedStrategy(NotificationStrategy):
    """Estrategia para notificar al profesor cuando recibe una calificación/review."""

    def get_title(self, data):
        return "Nueva Calificación Recibida"

    def get_message(self, data):
        rating = data['rating']
        student = rating.estudiante.user.get_full_name() or rating.estudiante.user.username
        course = rating.inscripcion.horario_ofertado.oferta.ramo.name
        stars = rating.puntuacion

        message = f"{student} te ha calificado con {'⭐' * stars} ({stars}/5) en tu clase de {course}"

        # Si hay comentario, agregar preview
        if rating.comentario:
            comment_preview = rating.comentario[:80] + "..." if len(rating.comentario) > 80 else rating.comentario
            message += f": '{comment_preview}'"
        else:
            message += "."
        
        return message

    def get_actions(self, notification):
        # Siempre intentar ofrecer navegación al perfil del calificado si existe
        if not notification.related_object:
            return []

        rating = notification.related_object
        # `calificado` es el perfil que recibe la calificación
        calificado = getattr(rating, 'calificado', None)
        if not calificado:
            return []

        profile_uid = getattr(calificado.user, 'public_uid', None)
        if not profile_uid:
            return []

        return [
            {
                'label': 'Ir a mi perfil',
                'url': reverse('accounts:profile_detail', args=[profile_uid]),
                'method': 'GET',
                'style': 'primary'
            }
        ]

    def get_icon(self):
        return "⭐"
