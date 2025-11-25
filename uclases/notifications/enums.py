"""
Constantes para tipos de notificaciones.

Define los tipos de notificaciones disponibles en el sistema como constantes
de string para uso en el código. Esto permite autocompletado y prevención de typos
sin requerir migrations cuando se agregan nuevos tipos.
"""


class NotificationTypes:
    """
    Tipos de notificaciones disponibles en el sistema.
    
    Estas constantes se usan para identificar el tipo de notificación
    al crearlas y para filtrarlas en queries.
    """
    # Notificaciones de inscripciones
    INSCRIPTION_CREATED = 'inscription_created'
    INSCRIPTION_ACCEPTED = 'inscription_accepted'
    INSCRIPTION_REJECTED = 'inscription_rejected'
    INSCRIPTION_CANCELED = 'inscription_canceled'
    # Notificación cuando un profesor propone una oferta en respuesta a una solicitud
    OFERTA_PROPOSED = 'oferta_proposed'
    INSCRIPTION_COMPLETED = 'inscription_completed'
    
    # Notificaciones de ofertas
    OFFER_DELETED = 'offer_deleted'
    
    # Notificaciones de comentarios
    NEW_COMMENT = 'new_comment'
    COMMENT_REPLY = 'comment_reply'
    OFFER_ON_REQUEST = 'offer_on_request'
    
    # Notificaciones de reviews
    RATING_RECEIVED = 'rating_received'
    
    # Notificaciones de cupos
    SLOTS_FULL = 'slots_full'
    
    # Notificaciones de recordatorios
    REMINDER_CLASS_SOON = 'reminder_class_soon'
