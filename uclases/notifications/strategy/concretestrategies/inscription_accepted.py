from notifications.strategy.trait import NotificationStrategy
from notifications.strategy.factory import NotificationStrategyFactory
from notifications.enums import NotificationTypes
from django.urls import reverse

@NotificationStrategyFactory.register(NotificationTypes.INSCRIPTION_ACCEPTED)
class InscriptionAcceptedStrategy(NotificationStrategy):
    """Estrategia de notificación para inscripciones aceptadas."""

    def get_title(self, data):
        return "Inscripción Aceptada"

    def get_message(self, data):
        inscription = data['inscripcion']
        offer = inscription.horario_ofertado.oferta.titulo
        teacher = inscription.horario_ofertado.oferta.profesor.user.get_full_name() or inscription.horario_ofertado.oferta.profesor.user.username
        course = inscription.horario_ofertado.oferta.ramo
        return f"Tu inscripción de la oferta llamada '{offer}' en el ramo '{course.name}' con el profesor '{teacher}' ha sido aceptada. ¡Bienvenido!"

    def get_actions(self, notification):
        if not notification.related_object:
            return []
        
        inscription = notification.related_object
        inscription_id = inscription.pk
        offer_id = inscription.horario_ofertado.oferta.pk
        teacher_uid = inscription.horario_ofertado.oferta.profesor.user.public_uid
        
        # Si ya se realizó una acción, solo mostrar botones de navegación
        if notification.action_taken:
            return [
                {
                    'label': 'Ver oferta',
                    'url': reverse('courses:oferta_detail', args=[offer_id]),
                    'method': 'GET',
                    'style': 'primary'
                },
                {
                    'label': 'Ver profesor',
                    'url': reverse('accounts:profile_detail', args=[teacher_uid]),
                    'method': 'GET',
                    'style': 'info'
                }
            ]
        
        # Si aún no se realizó acción, mostrar todos los botones
        return [
            {
                'label': 'Cancelar inscripción',
                'url': reverse('courses:cancelar_inscripcion', args=[inscription_id]),
                'method': 'POST',
                'style': 'danger'
            },
            {
                'label': 'Ver oferta',
                'url': reverse('courses:oferta_detail', args=[offer_id]),
                'method': 'GET',
                'style': 'primary'
            },
            {
                'label': 'Ver profesor',
                'url': reverse('accounts:profile_detail', args=[teacher_uid]),
                'method': 'GET',
                'style': 'info'
            }
        ]

    def get_icon(self):
        return "✅"