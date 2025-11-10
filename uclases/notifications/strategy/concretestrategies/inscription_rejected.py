from notifications.strategy.trait import NotificationStrategy
from notifications.strategy.factory import NotificationStrategyFactory
from notifications.enums import NotificationTypes
from django.urls import reverse

@NotificationStrategyFactory.register(NotificationTypes.INSCRIPTION_REJECTED)
class InscriptionRejectedStrategy(NotificationStrategy):
    """Estrategia para notificar al estudiante cuando su inscripción es rechazada."""

    def get_title(self, data):
        return "Inscripción Rechazada"

    def get_message(self, data):
        inscription = data['inscripcion']
        offer = inscription.horario_ofertado.oferta.titulo
        teacher = inscription.horario_ofertado.oferta.profesor.user.get_full_name() or inscription.horario_ofertado.oferta.profesor.user.username
        course = inscription.horario_ofertado.oferta.ramo.name
        
        return (f"Tu inscripción en la oferta '{offer}' del ramo {course} "
                f"con el profesor {teacher} ha sido rechazada.")

    def get_actions(self, notification):
        if not notification.related_object:
            return []
        
        inscription = notification.related_object
        course_name = inscription.horario_ofertado.oferta.ramo.name
        
        return [
            {
                'label': 'Ver otras ofertas',
                'url': reverse('courses:publications'),
                'method': 'GET',
                'style': 'primary'
            }
        ]

    def get_icon(self):
        return "❌"
