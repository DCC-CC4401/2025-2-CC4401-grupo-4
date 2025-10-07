from django.shortcuts import render
from courses.models import OfertaClase, SolicitudClase
from itertools import chain
from operator import attrgetter

def home(request):
    # Obtener todas las ofertas y solicitudes
    ofertas = OfertaClase.objects.all()
    solicitudes = SolicitudClase.objects.all()
    
    # Combinar ambas listas y ordenar por fecha de publicación (más recientes primero)
    publicaciones_recientes = sorted(
        chain(ofertas, solicitudes),
        key=attrgetter('fecha_publicacion'),
        reverse=True
    )
    
    context = {
        'publicaciones_recientes': publicaciones_recientes,
    }
    return render(request, 'home/home.html', context)