from itertools import chain
from operator import attrgetter

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Perfil
from courses.models import OfertaClase, SolicitudClase

def perfil_autocomplete_api(request):
    term = (request.GET.get("q", "") or "").strip()
    queryset = (
        Perfil.objects.select_related("user", "carrera")
        .order_by("user__username")
    )

    if term:
        queryset = queryset.filter(user__username__icontains=term)

    results = [
        {
            "id": str(perfil.user.public_uid),
            "label": f"{perfil.user.username}",
            "description": perfil.carrera.name if perfil.carrera else "Sin carrera",
        }
        for perfil in queryset[:10]
    ]

    return JsonResponse(results, safe=False)

def home(request):
    perfil_uid = request.GET.get("perfil")
    if perfil_uid:
        return redirect("accounts:profile_detail", public_uid=perfil_uid)

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