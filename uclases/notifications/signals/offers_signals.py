"""
Signals para notificaciones relacionadas con ofertas de clases.

Este módulo contiene signals que se disparan cuando ocurren eventos
relacionados con ofertas, como eliminación, edición, etc.
"""

from django.db.models.signals import pre_delete
from django.dispatch import receiver
from courses.models import OfertaClase
from courses.enums import EstadoInscripcion
from notifications.services.notification_service import NotificationService
from notifications.enums import NotificationTypes


@receiver(pre_delete, sender=OfertaClase)
def notify_students_on_offer_deletion(sender, instance, **kwargs):
    """
    Signal que se ejecuta antes de eliminar una OfertaClase.
    
    Notifica a todos los estudiantes con inscripciones activas (PENDIENTE o ACEPTADO)
    que la oferta ha sido eliminada y su inscripción cancelada.
    
    Args:
        sender: Modelo que envía la señal (OfertaClase)
        instance: Instancia de OfertaClase que será eliminada
        **kwargs: Argumentos adicionales del signal
    """
    # Obtener información de la oferta antes de que se elimine
    offer_title = instance.titulo
    course_name = instance.ramo.name if instance.ramo else ''
    professor_name = instance.profesor.user.get_full_name() or instance.profesor.user.username
    
    # Obtener todos los estudiantes con inscripciones activas
    estudiantes_inscritos = set()
    for horario in instance.horarios.all():
        inscripciones_activas = horario.inscripciones.filter(
            estado__in=[EstadoInscripcion.PENDIENTE, EstadoInscripcion.ACEPTADO]
        )
        for inscripcion in inscripciones_activas:
            estudiantes_inscritos.add(inscripcion.estudiante)
    
    # Notificar a cada estudiante inscrito
    for estudiante in estudiantes_inscritos:
        NotificationService.send(
            receiver=estudiante,
            type=NotificationTypes.OFFER_DELETED,
            data={
                'offer_title': offer_title,
                'course_name': course_name,
                'professor_name': professor_name,
            },
            related_object=None  # La oferta será eliminada, no podemos relacionarla
        )
