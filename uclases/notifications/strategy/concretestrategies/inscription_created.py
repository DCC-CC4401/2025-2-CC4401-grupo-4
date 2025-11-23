from notifications.strategy.trait import NotificationStrategy
from notifications.strategy.factory import NotificationStrategyFactory
from notifications.enums import NotificationTypes
from django.urls import reverse

@NotificationStrategyFactory.register(NotificationTypes.INSCRIPTION_CREATED)
class InscriptionCreatedStrategy(NotificationStrategy):
    """Estrategia para notificar al profesor cuando recibe una nueva inscripción."""

    def get_title(self, data):
        return "Nueva Inscripción"

    def get_message(self, data):
        inscription = data['inscripcion']
        student = inscription.estudiante.user.get_full_name() or inscription.estudiante.user.username
        offer = inscription.horario_ofertado.oferta.titulo
        course = inscription.horario_ofertado.oferta.ramo.name
        schedule = inscription.horario_ofertado
        day = schedule.get_dia_display()
        
        return (f"El estudiante {student} se ha inscrito en tu oferta '{offer}' "
                f"del ramo {course}. Horario: {day} {schedule.hora_inicio.strftime('%H:%M')} - "
                f"{schedule.hora_fin.strftime('%H:%M')}.")

    def get_actions(self, notification):
        if not notification.related_object:
            return []
        
        inscription = notification.related_object
        inscription_id = inscription.pk
        offer_id = inscription.horario_ofertado.oferta.pk
        student_uid = inscription.estudiante.user.public_uid
        
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
                    'label': 'Ver estudiante',
                    'url': reverse('accounts:profile_detail', args=[student_uid]),
                    'method': 'GET',
                    'style': 'info'
                }
            ]
        
        # Si aún no se realizó acción, mostrar todos los botones
        return [
            {
                'label': 'Aceptar',
                'url': reverse('courses:aceptar_inscripcion', args=[inscription_id]),
                'method': 'POST',
                'style': 'success'
            },
            {
                'label': 'Rechazar',
                'url': reverse('courses:rechazar_inscripcion', args=[inscription_id]),
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
                'label': 'Ver estudiante',
                'url': reverse('accounts:profile_detail', args=[student_uid]),
                'method': 'GET',
                'style': 'info'
            }
        ]

    def get_icon(self):
        return "📝"
