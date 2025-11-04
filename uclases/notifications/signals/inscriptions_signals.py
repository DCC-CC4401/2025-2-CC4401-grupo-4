from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from courses.models import Inscripcion
from courses.enums import EstadoInscripcion
from notifications.services.notification_service import NotificationService

@receiver(post_save, sender=Inscripcion)
def notify_inscription_created(sender, instance, created, **kwargs):
    if created and instance.estado == EstadoInscripcion.PENDIENTE:
        NotificationService.send(
            receiver=instance.horario_ofertado.oferta.profesor,
            type='inscription_created',
            data={'inscripcion': instance},
            related_object=instance
        )

@receiver(pre_save, sender=Inscripcion)
def notify_inscription_status_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            inscripcion_anterior = Inscripcion.objects.get(pk=instance.pk)
            if inscripcion_anterior.estado != instance.estado:
                if instance.estado == EstadoInscripcion.ACEPTADO:
                    NotificationService.send(
                        receiver=instance.estudiante,
                        type='inscription_accepted',
                        data={'inscripcion': instance},
                        related_object=instance
                    )
                elif instance.estado == EstadoInscripcion.RECHAZADO:
                    NotificationService.send(
                        receiver=instance.estudiante,
                        type='inscription_rejected',
                        data={'inscripcion': instance},
                        related_object=instance
                    )
                elif instance.estado == EstadoInscripcion.CANCELADO:
                    NotificationService.send(
                        receiver=instance.horario_ofertado.oferta.profesor,
                        type='inscription_canceled',
                        data={'inscripcion': instance},
                        related_object=instance
                    )
        except Inscripcion.DoesNotExist:
            pass