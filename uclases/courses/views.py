from itertools import chain
from operator import attrgetter

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .enums import DiaSemana
from .forms import HorarioFormSet, OfertaForm, SolicitudClaseForm
from .models import OfertaClase, SolicitudClase


def publications_view(request):
    """Listar todas las publicaciones (ofertas y solicitudes) ordenadas por fecha."""
    ofertas_qs = OfertaClase.objects.select_related('profesor__user', 'profesor__carrera').prefetch_related('ramos')
    solicitudes_qs = SolicitudClase.objects.select_related('solicitante__user', 'solicitante__carrera', 'ramo')
    
    publicaciones = sorted(
        chain(ofertas_qs, solicitudes_qs),
        key=attrgetter('fecha_publicacion'),
        reverse=True,
    )
    
    context = {
        'publicaciones': publicaciones,
    }
    return render(request, 'courses/publications_list.html', context)

def oferta_detail(request, pk):
    """Vista detallada de una oferta de clase"""
    oferta = get_object_or_404(OfertaClase, pk=pk)
    
    # Ordenar horarios por día de la semana (de lunes a domingo)
    horarios_ordenados = oferta.horarios.all().order_by('dia', 'hora_inicio')
    
    context = {
        'oferta': oferta,
        'horarios_ordenados': horarios_ordenados,
        'dias_semana': DiaSemana,
    }
    return render(request, 'courses/oferta_detail.html', context)


def solicitud_detail(request, pk):
    """Vista detallada de una solicitud de clase"""
    solicitud = get_object_or_404(SolicitudClase, pk=pk)
    
    context = {
        'solicitud': solicitud,
    }
    return render(request, 'courses/solicitud_detail.html', context)

def crear_oferta(request):
    if request.method == "POST":
        form = OfertaForm(request.POST)
        if form.is_valid():
            oferta = form.save(commit=False)  # guarda el padre
            oferta.profesor = request.user.perfil
            oferta.save()
            form.save_m2m()
            formset = HorarioFormSet(request.POST, instance=oferta, prefix="horarios")
            if formset.is_valid():
                formset.save()
                messages.success(request, "Oferta y horarios creados correctamente.")
                return redirect('/', pk=oferta.pk)
        else:
            formset = HorarioFormSet(prefix="horarios")
    else:
        form = OfertaForm()
        formset = HorarioFormSet(prefix="horarios")

    return render(request, "courses/crear_oferta.html", {"form": form, "formset": formset})


def crear_solicitud(request):
    if request.method == "POST":
        form = SolicitudClaseForm(request.POST)
        if form.is_valid():
            solicitud = form.save()
            solicitud.solicitante = request.user.perfil
            solicitud.save()
            messages.success(request, "Solicitud creada correctamente.")
            return redirect('/', pk=solicitud.pk)
    else:
        form = SolicitudClaseForm()

    return render(request, "courses/crear_solicitud.html", {"form": form})