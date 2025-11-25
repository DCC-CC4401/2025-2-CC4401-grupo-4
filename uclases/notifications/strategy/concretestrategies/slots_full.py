from notifications.strategy.trait import NotificationStrategy
from notifications.strategy.factory import NotificationStrategyFactory
from notifications.enums import NotificationTypes
from django.urls import reverse

@NotificationStrategyFactory.register(NotificationTypes.SLOTS_FULL)
class SlotsFullStrategy(NotificationStrategy):
    """Estrategia para notificar al profesor cuando se agotan los cupos de un horario."""

    def get_title(self, data):
        return ""

    def get_message(self, data):
        schedule = data['horario']
        offer = schedule.oferta
        day = schedule.get_dia_display()
        start_time = schedule.hora_inicio.strftime('%H:%M')
        end_time = schedule.hora_fin.strftime('%H:%M')
        
        return (f"¡Todos los cupos del horario {day} ({start_time} - {end_time}) "
                f"de tu oferta '{offer.titulo}' están llenos! 🎉")

    def get_actions(self, notification):
        if not notification.related_object:
            return []

        schedule = notification.related_object
        offer = getattr(schedule, 'oferta', None)
        if not offer and hasattr(schedule, 'pk') and schedule.__class__.__name__ in ('OfertaClase', 'Oferta'):
            offer = schedule

        if not offer:
            return []

        offer_id = getattr(offer, 'pk', None)
        if not offer_id:
            return []

        return [
            {
                'label': 'Ver oferta',
                'url': reverse('courses:oferta_detail', args=[offer_id]),
                'method': 'GET',
                'style': 'primary'
            }
        ]

    def get_icon(self):
        return "🎉"
