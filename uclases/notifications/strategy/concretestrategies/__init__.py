"""
Módulo de estrategias concretas de notificaciones.

Cada estrategia implementa la interfaz NotificationStrategy
y se registra automáticamente en el factory mediante el decorador @register.
"""

# Importar todas las estrategias para que se registren automáticamente
from . import inscription_created
from . import inscription_accepted
from . import inscription_rejected
from . import inscription_canceled
from . import oferta_proposed

