from abc import ABC, abstractmethod

class NotificationStrategy(ABC):

    @abstractmethod
    def get_icon(self):
        """Retorna el ícono asociado a la notificación"""
        pass

    @abstractmethod
    def get_title(self, data):
        """Genera el título de la notificación basado en los datos proporcionados"""
        pass

    @abstractmethod
    def get_message(self, data):
        """Genera el mensaje de la notificación basado en los datos proporcionados"""
        pass

    @abstractmethod
    def get_actions(self, notification):
        """Genera las acciones asociadas a la notificación"""
        pass