from notifications.strategy.trait import NotificationStrategy
from notifications.strategy.factory import NotificationStrategyFactory

@NotificationStrategyFactory.register('inscription_accepted')
class InscriptionAcceptedStrategy(NotificationStrategy):
    """Estrategia de notificación para inscripciones aceptadas."""

    def get_title(self, data):
        return "Inscripción Aceptada"

    def get_message(self, data):
        ramo = data.get('ramo')
        return f"Tu inscripción en el ramo '{ramo.name}' ha sido aceptada. ¡Bienvenido!"

    def get_actions(self, notification):
        if not notification.related_object:
            return []
        oferta = notification.related_object.horario_ofertado.oferta
        return [dict(label=f"url:/ofertas/{oferta.id}", 
                     url=f"/ofertas/{oferta.id}",
                     method="GET",
                     style="primary")]

    def get_icon(self):  # ✅ Nombre correcto
        return "✅"