"""
Signals para el sistema de notificaciones.

Este módulo importa todos los signals para que se registren automáticamente
cuando Django inicia la aplicación.
"""

# Importar todos los módulos de signals para que se registren
from . import inscriptions_signals
from . import slots_signals
from . import comments_signals
from . import ratings_signals
from . import offers_signals

# Al agregar nuevos signals, importarlos aquí:
