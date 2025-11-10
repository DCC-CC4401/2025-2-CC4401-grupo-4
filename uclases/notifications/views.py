from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def notifications_view(request):
    """
    Muestra todas las notificaciones del usuario.
    El orden está definido en el modelo Notification (más recientes primero).
    """
    notifications = request.user.perfil.notifications.all()
    
    context = {
        'notifications': notifications
    }
    return render(request, 'notifications/notifications_detail.html', context)