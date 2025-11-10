from .fallback import NotificationStrategyFallback

class NotificationStrategyFactory:
    """Fábrica para obtener estrategias de notificación según el tipo"""

    # Diccionario de estrategias registradas, se llena mediante el decorador register
    _strategies = {
    }

    @classmethod
    def register(cls, key):
        """Decorator para registrar una estrategia de notificación de una forma mas sencilla"""

        def decorator(strategy_cls):
            cls._strategies[key] = strategy_cls()
            return strategy_cls

        return decorator
    
    @classmethod
    def get_strategy(cls, key):
        """Obtiene la estrategia de notificación correspondiente al key dado, si no existe, retorna la estrategia por defecto."""
        # Las estrategias ya están instanciadas en _strategies
        return cls._strategies.get(key, NotificationStrategyFallback())