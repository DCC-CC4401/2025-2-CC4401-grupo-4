"""
Módulo de estrategias concretas de notificaciones.

Cada estrategia implementa la interfaz NotificationStrategy
y se registra automáticamente en el factory mediante el decorador @register.
"""

# Importar todas las estrategias para que se registren automáticamente
from . import inscription_accepted

# Al agregar nuevas estrategias, importarlas de la misma manera que la anterior:

