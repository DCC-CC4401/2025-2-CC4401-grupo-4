from django.db import models

class TipoNotificacion(models.TextChoices):
    """Tipos de notificaciones disponibles en el sistema"""
    INSCRIPCION_PENDIENTE = 'inscripcion_pendiente', 'Inscripción Pendiente'
    INSCRIPCION_ACEPTADA = 'inscripcion_aceptada', 'Inscripción Aceptada'
    INSCRIPCION_RECHAZADA = 'inscripcion_rechazada', 'Inscripción Rechazada'
    INSCRIPCION_CANCELADA = 'inscripcion_cancelada', 'Inscripción Cancelada'
