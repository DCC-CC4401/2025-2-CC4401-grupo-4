from itertools import chain
from operator import attrgetter

from django.http import JsonResponse
from django.shortcuts import redirect, render

from accounts.models import Perfil
from courses.models import OfertaClase, SolicitudClase

def perfil_autocomplete_api(request):
    """
    API de autocompletado que busca perfiles de usuarios por nombre de usuario.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP con parámetro 'q' en GET para búsqueda.
    
    Returns:
        JsonResponse: Lista JSON con los primeros 10 perfiles que coinciden con el término.
                      Cada elemento contiene id (UUID), label (username) y description (carrera).
    
    Dependencies:
        - accounts.models.Perfil
        - django.http.JsonResponse
    """
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
    """
    Vista principal que muestra las publicaciones recientes (ofertas y solicitudes de clases).
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP. Si incluye parámetro 'perfil' en GET,
                               redirige al perfil del usuario especificado.
    
    Returns:
        HttpResponse: Renderiza la página principal con las 5 publicaciones más recientes.
        HttpResponseRedirect: Redirige al perfil si se proporciona 'perfil_uid' en GET.
    
    Template:
        'home/home.html'
    
    Dependencies:
        - courses.models (OfertaClase, SolicitudClase)
        - itertools.chain, operator.attrgetter
    """
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