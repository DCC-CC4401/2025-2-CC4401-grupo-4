from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import OfertaClase, SolicitudClase
from .enums import DiaSemana
from .forms import OfertaForm, HorarioFormSet

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
    """Vista para crear una nueva oferta de clase"""
    if request.method == "POST":
        form = OfertaForm(request.POST)
        formset = HorarioFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            oferta = form.save()
            horarios = formset.save(commit=False)
            for h in horarios:
                h.oferta = oferta  # vincula el horario con la oferta
                h.save()
            messages.success(request, "Oferta y horarios creados correctamente.")
            return redirect('oferta_detail', pk=oferta.pk)
    else:
        form = OfertaForm()
        formset = HorarioFormSet()
        

    context = {"form": form, "formset": formset}
    return render(request, "courses/crear_oferta.html", context)