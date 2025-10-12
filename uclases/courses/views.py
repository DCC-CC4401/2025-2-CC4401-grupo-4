from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import OfertaClase, SolicitudClase
from .enums import DiaSemana
from .forms import OfertaForm, HorarioFormSet, SolicitudClaseForm

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
            solicitud = form.save(commit=False)
            solicitud.solicitante = request.user.perfil
            solicitud.save()
            messages.success(request, "Solicitud creada correctamente.")
            return redirect('/', pk=solicitud.pk)
    else:
        form = SolicitudClaseForm()

    return render(request, "courses/crear_solicitud.html", {"form": form})


@login_required
def editar_oferta(request, pk):
    oferta = get_object_or_404(OfertaClase, pk=pk)
    if oferta.profesor != request.user.perfil:
        messages.error(request, "No tienes permiso para editar esta oferta.")
        return redirect('courses:oferta_detail', pk=pk)

    if request.method == "POST":
        form = OfertaForm(request.POST, instance=oferta)
        formset = HorarioFormSet(request.POST, instance=oferta, prefix="horarios")
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Oferta actualizada correctamente.")
            return redirect('courses:oferta_detail', pk=oferta.pk)
    else:
        form = OfertaForm(instance=oferta)
        formset = HorarioFormSet(instance=oferta, prefix="horarios")

    return render(request, "courses/editar_oferta.html", {"form": form, "formset": formset, "oferta": oferta})

@login_required
def editar_solicitud(request, pk):
    solicitud = get_object_or_404(SolicitudClase, pk=pk)
    if solicitud.solicitante != request.user.perfil:
        messages.error(request, "No tienes permiso para editar esta solicitud.")
        return redirect('courses:solicitud_detail', pk=pk)

    if request.method == "POST":
        form = SolicitudClaseForm(request.POST, instance=solicitud)
        if form.is_valid():
            form.save()
            messages.success(request, "Solicitud actualizada correctamente.")
            return redirect('courses:solicitud_detail', pk=solicitud.pk)
    else:
        form = SolicitudClaseForm(instance=solicitud)

    return render(request, "courses/editar_solicitud.html", {"form": form, "solicitud": solicitud})