from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages

from accounts.models import Perfil
from .models import OfertaClase, SolicitudClase, Ramo
from .enums import DiaSemana
from .forms import OfertaForm, HorarioFormSet, SolicitudClaseForm


def ramo_autocomplete_api(request):
    """Retorna coincidencias de ramos en formato JSON."""

    term = (request.GET.get("q", "") or "").strip()
    perfil = request.user.perfil
    ramos = perfil.ramos_cursados.all().order_by("name")

    if term:
        ramos = ramos.filter(name__icontains=term)

    results = [
        {
            "id": ramo.id,
            "label": ramo.name,
        }
        for ramo in ramos[:15]
    ]
    return JsonResponse(results, safe=False)

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