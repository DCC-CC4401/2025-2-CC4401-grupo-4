from itertools import chain
from operator import attrgetter

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from accounts.models import Perfil
from .models import OfertaClase, SolicitudClase, Ramo, HorarioOfertado, Inscripcion
from .enums import DiaSemana, EstadoInscripcion
from .forms import HorarioFormSet, OfertaForm, SolicitudClaseForm


def publications_view(request):
    """Listar todas las publicaciones (ofertas y solicitudes) ordenadas por fecha."""
    ofertas_qs = OfertaClase.objects.select_related('profesor__user', 'profesor__carrera', 'ramo')
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

@login_required
def crear_oferta(request):
    if request.method == "POST":
        form = OfertaForm(request.POST, user=request.user)
        formset = HorarioFormSet(request.POST, prefix="horarios")
        
        if form.is_valid() and formset.is_valid():
            oferta = form.save(commit=False)
            oferta.profesor = request.user.perfil
            oferta.save()
            form.save_m2m()
            
            # Asociar el formset con la oferta creada
            formset.instance = oferta
            formset.save()
            
            messages.success(request, "Oferta y horarios creados correctamente.")
            return redirect('courses:oferta_detail', pk=oferta.pk)
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = OfertaForm(user=request.user)
        formset = HorarioFormSet(prefix="horarios")

    return render(request, "courses/crear_oferta.html", {"form": form, "formset": formset})


@login_required
def crear_solicitud(request):
    if request.method == "POST":
        form = SolicitudClaseForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.solicitante = request.user.perfil
            solicitud.save()
            messages.success(request, "Solicitud creada correctamente.")
            return redirect('courses:solicitud_detail', pk=solicitud.pk)
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
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
        form = OfertaForm(request.POST, instance=oferta, user=request.user)
        formset = HorarioFormSet(request.POST, instance=oferta, prefix="horarios")
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Oferta actualizada correctamente.")
            return redirect('courses:oferta_detail', pk=oferta.pk)
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = OfertaForm(instance=oferta, user=request.user)
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
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = SolicitudClaseForm(instance=solicitud)

    return render(request, "courses/editar_solicitud.html", {"form": form, "solicitud": solicitud})


def inscribirse_view(request, pk):
    """Vista para que un estudiante seleccione un horario y se inscriba"""
    oferta = get_object_or_404(OfertaClase, pk=pk)
    horarios_ordenados = oferta.horarios.all().order_by('dia', 'hora_inicio')

    if request.method == "POST":
        horario_id = request.POST.get("horario")
        horario = get_object_or_404(HorarioOfertado, id=horario_id, oferta=oferta)

        # Verificar cupos
        inscripciones_activas = horario.inscripciones.filter(
            estado__in=[0, 1]  # Pendiente o Aceptado
        ).count()

        if inscripciones_activas >= horario.cupos_totales:
            messages.error(request, "Lo sentimos, este horario ya no tiene cupos disponibles.")
            return redirect("inscribirse", pk=oferta.pk)

        # Crear inscripción
        inscripcion, created = Inscripcion.objects.get_or_create(
            estudiante=request.user.perfil,
            horario_ofertado=horario,
        )

        if not created:
            messages.warning(request, "Ya estás inscrito en este horario.")
        else:
            # Reducir cupos solo si se crea una nueva inscripción
            horario.cupos_totales -= 1
            horario.save()
            inscripcion.aceptar()
            messages.success(request, "¡Inscripción completada con éxito!")

        return redirect("courses:oferta_detail", pk=oferta.pk)

    context = {
        "oferta": oferta,
        "horarios_ordenados": horarios_ordenados,
    }
    return render(request, "courses/inscribirse.html", context)