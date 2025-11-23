"""
Context processors para el módulo de notificaciones.
Hace disponibles datos de notificaciones en todos los templates.
"""

def unread_notifications(request):
    """
    Agrega el contador de notificaciones no leídas al contexto global.
    
    Disponible en todos los templates como {{ unread_notifications_count }}
    
    Args:
        request: HttpRequest object
        
    Returns:
        dict: Diccionario con el contador de notificaciones no leídas
    """
    if request.user.is_authenticated and hasattr(request.user, 'perfil'):
        count = request.user.perfil.notifications.filter(read=False).count()
        return {
            'unread_notifications_count': count
        }
    
    return {
        'unread_notifications_count': 0
    }
