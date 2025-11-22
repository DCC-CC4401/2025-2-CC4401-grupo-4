from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

@login_required
def notifications_view(request):
    """
    Muestra todas las notificaciones del usuario con paginación.
    El orden está definido en el modelo Notification (más recientes primero).
    Optimizado con select_related y prefetch_related para evitar N+1 queries.
    """
    notifications_list = request.user.perfil.notifications.select_related(
        'content_type'
    ).prefetch_related(
        'related_object'
    ).all()
    
    # Paginación: 15 notificaciones por página
    paginator = Paginator(notifications_list, 15)
    page_number = request.GET.get('page', 1)
    notifications = paginator.get_page(page_number)
    
    context = {
        'notifications': notifications
    }
    return render(request, 'notifications/notifications_detail.html', context)