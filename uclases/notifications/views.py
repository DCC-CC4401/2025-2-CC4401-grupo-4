from django.shortcuts import render

def notifications_view(request):
    # Para mostrar las notificaciones
    notifications = request.user.notifications.all()
    context = {
        'notifications': notifications
    }
    return render(request, 'notifications/notifications_detail.html', context)