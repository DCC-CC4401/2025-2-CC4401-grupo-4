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
from . import oferta_proposed
from . import inscription_completed

# Notificaciones de ofertas
from . import offer_deleted

# Notificaciones de comentarios
from . import new_comment

# Notificaciones de reviews
from . import rating_received

# Notificaciones de cupos
from . import slots_full

