from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from .models import Notification

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


@login_required
@require_POST
def mark_as_read(request, notification_id):
    """
    Marca una notificación específica como leída.
    Solo el receptor puede marcar sus propias notificaciones.
    Soporta AJAX para no recargar la página.
    """
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        receiver=request.user.perfil
    )
    
    notification.read = True
    notification.save()
    
    # Si es una petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        unread_count = request.user.perfil.notifications.filter(read=False).count()
        return JsonResponse({
            'success': True,
            'is_read': True,
            'new_url': reverse('notifications:mark_unread', args=[notification_id]),
            'unread_count': unread_count
        })
    
    messages.success(request, 'Notificación marcada como leída.')
    return redirect('notifications:list')


@login_required
@require_POST
def mark_as_unread(request, notification_id):
    """
    Marca una notificación específica como NO leída.
    Solo el receptor puede marcar sus propias notificaciones.
    Soporta AJAX para no recargar la página.
    """
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        receiver=request.user.perfil
    )
    
    notification.read = False
    notification.save()
    
    # Si es una petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        unread_count = request.user.perfil.notifications.filter(read=False).count()
        return JsonResponse({
            'success': True,
            'is_read': False,
            'new_url': reverse('notifications:mark_read', args=[notification_id]),
            'unread_count': unread_count
        })
    
    messages.success(request, 'Notificación marcada como no leída.')
    return redirect('notifications:list')


@login_required
@require_POST
def mark_all_as_read(request):
    """
    Marca todas las notificaciones no leídas del usuario como leídas.
    Usa update() para ser eficiente con la base de datos.
    Soporta AJAX para no recargar la página.
    """
    count = request.user.perfil.notifications.filter(read=False).update(read=True)
    
    # Si es una petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if count > 0:
            return JsonResponse({
                'success': True,
                'count': count,
                'message': f'{count} notificación(es) marcada(s) como leída(s).'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'No hay notificaciones sin leer.'
            })
    
    if count > 0:
        messages.success(request, f'{count} notificación(es) marcada(s) como leída(s).')
    else:
        messages.info(request, 'No hay notificaciones sin leer.')
    
    return redirect('notifications:list')