from notifications.strategy.trait import NotificationStrategy
from notifications.strategy.factory import NotificationStrategyFactory
from notifications.enums import NotificationTypes
from django.urls import reverse

@NotificationStrategyFactory.register(NotificationTypes.REMINDER_CLASS_SOON)
class ReminderClassSoonStrategy(NotificationStrategy):
    """Estrategia para recordar una clase próxima."""

    def get_title(self, data):
        return ""

    def get_message(self, data):
        inscription = data['inscripcion']
        schedule = inscription.horario_ofertado
        offer = schedule.oferta
        day = schedule.get_dia_display()
        
        # Determinar si es profesor o estudiante quien recibe
        is_teacher = data.get('is_teacher', False)
        
        if is_teacher:
            student = inscription.estudiante.user.get_full_name() or inscription.estudiante.user.username
            return (f"Recordatorio: Mañana tienes clase de {offer.ramo.name} "
                    f"con {student} a las {schedule.hora_inicio.strftime('%H:%M')}.")
        else:
            teacher = offer.profesor.user.get_full_name() or offer.profesor.user.username
            return (f"Recordatorio: Mañana tienes clase de {offer.ramo.name} "
                    f"con el profesor {teacher} a las {schedule.hora_inicio.strftime('%H:%M')}.")

    def get_actions(self, notification):
        return []

    def get_icon(self):
        return "⏰"
