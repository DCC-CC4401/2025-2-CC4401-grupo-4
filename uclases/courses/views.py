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
    if request.method == "POST":
        form = OfertaForm(request.POST)
        if form.is_valid():
            oferta = form.save()  # guarda el padre
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