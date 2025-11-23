from notifications.strategy.trait import NotificationStrategy
from notifications.strategy.factory import NotificationStrategyFactory
from notifications.enums import NotificationTypes
from django.urls import reverse

@NotificationStrategyFactory.register(NotificationTypes.INSCRIPTION_COMPLETED)
class InscriptionCompletedStrategy(NotificationStrategy):
    """Estrategia para notificar al estudiante cuando completa una clase."""

    def get_title(self, data):
        return ""

    def get_message(self, data):
        inscription = data['inscripcion']
        offer = inscription.horario_ofertado.oferta
        course = offer.ramo.name
        teacher = offer.profesor.user.get_full_name() or offer.profesor.user.username
        
        return (f"¡Has completado la clase de {course} con el profesor {teacher}! "
                f"Ayúdanos a mejorar calificando tu experiencia.")

    def get_actions(self, notification):
        return []

    def get_icon(self):
        return "🎓"
