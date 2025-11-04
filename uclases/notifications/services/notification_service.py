from notifications.models import Notification
from notifications.strategy.factory import NotificationStrategyFactory

class NotificationService:
    @staticmethod
    def send(receiver, type, data, related_object=None):
        """
        Envía una notificación utilizando la estrategia especificada.

        :param receiver: Usuario que recibirá la notificación.
        :param type: Identificador de la estrategia de notificación.
        :param data: Diccionario con los datos necesarios para la estrategia.
        :param related_object: Objeto relacionado con la notificación.
        """
        # Obtener la estrategia desde la fábrica
        strategy = NotificationStrategyFactory.get_strategy(type)

        # Crear la notificación
        Notification.objects.create(
            receiver=receiver,
            type=type,
            title=strategy.get_title(data),
            message=strategy.get_message(data),
            related_object=related_object
        )