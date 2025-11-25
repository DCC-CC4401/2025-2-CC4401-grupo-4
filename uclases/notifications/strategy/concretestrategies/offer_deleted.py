from notifications.strategy.trait import NotificationStrategy
from notifications.strategy.factory import NotificationStrategyFactory
from notifications.enums import NotificationTypes
from django.urls import reverse

@NotificationStrategyFactory.register(NotificationTypes.OFFER_DELETED)
class OfferDeletedStrategy(NotificationStrategy):
    """Estrategia para notificar a estudiantes cuando un profesor elimina una oferta."""

    def get_title(self, data):
        
        return "Clase cancelada por el profesor"

    def get_message(self, data):
        offer_title = data.get('offer_title', 'la clase')
        course_name = data.get('course_name', '')
        professor_name = data.get('professor_name', 'El profesor')
        
        message = f"{professor_name} ha eliminado la oferta '{offer_title}'"
        if course_name:
            message += f" de {course_name}"
        message += ". Tu inscripción ha sido cancelada automáticamente."
        
        return message

    def get_actions(self, notification):
        """
        Acciones disponibles para esta notificación.
        Como la oferta fue eliminada, solo mostramos una acción para buscar otras clases.
        """
        return [
            {
                'label': 'Buscar otras clases',
                'url': reverse('courses:publications'),
                'method': 'GET',
                'style': 'primary'
            }
        ]

    def get_icon(self):
        return "❌"
