from notifications.strategy.trait import NotificationStrategy
from notifications.strategy.factory import NotificationStrategyFactory
from django.urls import reverse

@NotificationStrategyFactory.register('inscription_rejected')
class InscriptionRejectedStrategy(NotificationStrategy):
    """Estrategia para notificar al estudiante cuando su inscripción es rechazada."""

    def get_title(self, data):
        return "Inscripción Rechazada"

    def get_message(self, data):
        inscription = data['inscripcion']
        oferta = inscription.horario_ofertado.oferta.titulo
        profesor = inscription.horario_ofertado.oferta.profesor.user.get_full_name() or inscription.horario_ofertado.oferta.profesor.user.username
        ramo = inscription.horario_ofertado.oferta.ramo.name
        
        return (f"Tu inscripción en la oferta '{oferta}' del ramo {ramo} "
                f"con el profesor {profesor} ha sido rechazada.")

    def get_actions(self, notification):
        if not notification.related_object:
            return []
        
        inscription = notification.related_object
        ramo_nombre = inscription.horario_ofertado.oferta.ramo.name
        
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
