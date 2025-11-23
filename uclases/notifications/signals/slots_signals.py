from django.db.models.signals import post_save
from django.dispatch import receiver
from courses.models import Inscripcion, HorarioOfertado
from courses.enums import EstadoInscripcion
from notifications.services.notification_service import NotificationService
from notifications.enums import NotificationTypes


@receiver(post_save, sender=HorarioOfertado)
def notify_slots_full(sender, instance, **kwargs):
    """
    Notifica al profesor cuando se llenan los cupos de un horario.
    
    Se dispara cuando un HorarioOfertado se actualiza y verifica si
    los cupos llegaron a 0.
    """
    # Verificar si se llenaron los cupos (cupos_totales == 0)
    if instance.cupos_totales == 0:
        # Verificar que hay al menos una inscripción aceptada en este horario
        # para evitar notificar si el horario fue creado con 0 cupos
        if instance.inscripciones.filter(estado=EstadoInscripcion.ACEPTADO).exists():
            # Enviar notificación al profesor
            NotificationService.send(
                receiver=instance.oferta.profesor,
                type=NotificationTypes.SLOTS_FULL,
                data={'horario': instance, 'oferta': instance.oferta},
                related_object=instance
            )
