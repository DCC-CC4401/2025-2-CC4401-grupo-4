from django.shortcuts import render
from courses.models import OfertaClase, SolicitudClase
from itertools import chain
from operator import attrgetter


def home(request):
   
    ofertas_qs = OfertaClase.objects.order_by('-fecha_publicacion')
    solicitudes_qs = SolicitudClase.objects.order_by('-fecha_publicacion')

    publicaciones_recientes_all = sorted(
        chain(ofertas_qs, solicitudes_qs),
        key=attrgetter('fecha_publicacion'),
        reverse=True,
    )

    publicaciones_recientes = publicaciones_recientes_all[:5]

    context = {
        'publicaciones_recientes': publicaciones_recientes,
        'mostrar_ver_todas': len(publicaciones_recientes_all) > len(publicaciones_recientes),
    }
    return render(request, 'home/home.html', context)