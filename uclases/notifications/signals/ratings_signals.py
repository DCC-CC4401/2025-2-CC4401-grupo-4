from django.db.models.signals import post_save
from django.dispatch import receiver
from courses.models import Rating
from notifications.services.notification_service import NotificationService
from notifications.enums import NotificationTypes

@receiver(post_save, sender=Rating)
def notify_new_rating(sender, instance, created, **kwargs):
    """Notifica al profesor cuando recibe una nueva calificación."""
    if not created:
        return

    # Obtener el profesor (destinatario de la notificación)
    profesor = instance.calificado

    NotificationService.send(
        receiver=profesor,
        type=NotificationTypes.RATING_RECEIVED,
        data={'calificacion': instance},
        related_object=instance
    )