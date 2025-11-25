from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from courses.models import Comentario
from notifications.services.notification_service import NotificationService
from notifications.enums import NotificationTypes

@receiver(post_save, sender=Comentario)
def notify_new_comment(sender, instance, created, **kwargs):
    if not created:
        return

    # Determinar dueño de la publicación (oferta o solicitud)
    publication_owner = None
    if instance.oferta_clase:
        publication_owner = instance.oferta_clase.profesor
    elif instance.solicitud_clase:
        publication_owner = instance.solicitud_clase.solicitante

    # Si no hay dueño conocido, o el autor del comentario es el dueño, no notificar
    if not publication_owner or publication_owner == instance.publicador:
        return

    NotificationService.send(
        receiver=publication_owner,
        type=NotificationTypes.NEW_COMMENT,
        data={'comentario': instance},
        related_object=instance
    )