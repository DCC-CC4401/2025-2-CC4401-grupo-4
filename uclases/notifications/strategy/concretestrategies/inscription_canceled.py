from notifications.strategy.trait import NotificationStrategy
from notifications.strategy.factory import NotificationStrategyFactory
from notifications.enums import NotificationTypes
from django.urls import reverse

@NotificationStrategyFactory.register(NotificationTypes.INSCRIPTION_CANCELED)
class InscriptionCanceledStrategy(NotificationStrategy):
    """Estrategia para notificar al profesor cuando un estudiante cancela su inscripción."""

    def get_title(self, data):
        return "Inscripción Cancelada"

    def get_message(self, data):
        inscription = data['inscripcion']
        estudiante = inscription.estudiante.user.get_full_name() or inscription.estudiante.user.username
        oferta = inscription.horario_ofertado.oferta.titulo
        ramo = inscription.horario_ofertado.oferta.ramo.name
        horario = inscription.horario_ofertado
        dia = horario.get_dia_display()
        
        return (f"El estudiante {estudiante} ha cancelado su inscripción en tu oferta "
                f"'{oferta}' del ramo {ramo}. Horario liberado: {dia} "
                f"{horario.hora_inicio.strftime('%H:%M')} - {horario.hora_fin.strftime('%H:%M')}.")

    def get_actions(self, notification):
        if not notification.related_object:
            return []
        
        inscription = notification.related_object
        oferta_id = inscription.horario_ofertado.oferta.pk
        
        return [
            {
                'label': 'Ver oferta',
                'url': reverse('courses:oferta_detail', args=[oferta_id]),
                'method': 'GET',
                'style': 'primary'
            }
        ]

    def get_icon(self):
        return "🚫"
