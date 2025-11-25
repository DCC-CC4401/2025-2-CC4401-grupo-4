from notifications.strategy.trait import NotificationStrategy
from notifications.strategy.factory import NotificationStrategyFactory
from notifications.enums import NotificationTypes
from django.urls import reverse

@NotificationStrategyFactory.register(NotificationTypes.OFERTA_PROPOSED)
class OfertaProposedStrategy(NotificationStrategy):
    """Estrategia para notificar al estudiante cuando se le propone una oferta de clase."""

    def get_title(self, data):
        return "Nueva Propuesta de Oferta de Clase"

    def get_message(self, data):
        oferta = data['oferta']
        profesor = oferta.profesor.user.get_full_name() or oferta.profesor.user.username
        ramo = oferta.ramo.name
        
        return (f"El profesor {profesor} te ha propuesto una nueva oferta de clase "
                f"para el ramo {ramo}: '{oferta.titulo}'.")

    def get_actions(self, notification):
        if not notification.related_object:
            return []
        
        oferta = notification.related_object
        oferta_id = oferta.pk
        profesor_uid = oferta.profesor.user.public_uid
        
        # Si ya se realizó una acción, solo mostrar botones de navegación
        if notification.action_taken:
            return [
                {
                    'label': 'Ver oferta',
                    'url': reverse('courses:oferta_detail', args=[oferta_id]),
                    'method': 'GET',
                    'style': 'primary'
                },
                {
                    'label': 'Ver profesor',
                    'url': reverse('accounts:profile_detail', args=[profesor_uid]),
                    'method': 'GET',
                    'style': 'info'
                }
            ]
        
        # Si aún no se realizó acción, mostrar todos los botones
        return [
            {
                'label': 'Ver oferta',
                'url': reverse('courses:oferta_detail', args=[oferta_id]),
                'method': 'GET',
                'style': 'primary'
            },
            {
                'label': 'Ver profesor',
                'url': reverse('accounts:profile_detail', args=[profesor_uid]),
                'method': 'GET',
                'style': 'info'
            }
        ]
    
    def get_icon(self):
        return "📬"