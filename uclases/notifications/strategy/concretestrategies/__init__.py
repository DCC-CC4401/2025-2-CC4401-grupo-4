"""
Módulo de estrategias concretas de notificaciones.

Cada estrategia implementa la interfaz NotificationStrategy
y se registra automáticamente en el factory mediante el decorador @register.
"""

# Importar todas las estrategias para que se registren automáticamente
# Notificaciones de inscripciones
from . import inscription_created
from . import inscription_accepted
from . import inscription_rejected
from . import inscription_canceled
from . import inscription_completed

# Notificaciones de comentarios
from . import new_comment
from . import comment_reply
from . import offer_on_request

# Notificaciones de reviews
from . import rating_received

# Notificaciones de cupos
from . import slots_full

# Notificaciones de recordatorios
from . import reminder_class_soon

