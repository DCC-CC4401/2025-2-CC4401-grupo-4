from notifications.strategy.trait import NotificationStrategy
from notifications.strategy.factory import NotificationStrategyFactory
from notifications.enums import NotificationTypes
from django.urls import reverse

@NotificationStrategyFactory.register(NotificationTypes.INSCRIPTION_CANCELED)
class InscriptionCanceledStrategy(NotificationStrategy):
    """Estrategia para notificar al profesor cuando un estudiante cancela su inscripción."""

    def get_title(self, data):
        return "Inscripción cancelada"

    def get_message(self, data):
        inscription = data['inscripcion']
        student = inscription.estudiante.user.get_full_name() or inscription.estudiante.user.username
        offer = inscription.horario_ofertado.oferta.titulo
        course = inscription.horario_ofertado.oferta.ramo.name
        schedule = inscription.horario_ofertado
        day = schedule.get_dia_display()
        
        return (f"El estudiante {student} ha cancelado su inscripción en tu oferta "
                f"'{offer}' del ramo {course}. Horario liberado: {day} "
                f"{schedule.hora_inicio.strftime('%H:%M')} - {schedule.hora_fin.strftime('%H:%M')}.")

    def get_actions(self, notification):
        if not notification.related_object:
            return []
        
        inscription = notification.related_object
        offer_id = inscription.horario_ofertado.oferta.pk
        
        return [
            {
                'label': 'Ver oferta',
                'url': reverse('courses:oferta_detail', args=[offer_id]),
                'method': 'GET',
                'style': 'primary'
            }
        ]

    def get_icon(self):
        return "🚫"
