from django.db import models

class NotificationTypes(models.TextChoices):
    # Notificaciones de inscripciones
    INSCRIPTION_CREATED = 'inscription_created', 'Nueva Inscripción'
    INSCRIPTION_ACCEPTED = 'inscription_accepted', 'Inscripción Aceptada'
    INSCRIPTION_REJECTED = 'inscription_rejected', 'Inscripción Rechazada'
    INSCRIPTION_CANCELED = 'inscription_canceled', 'Inscripción Cancelada'
