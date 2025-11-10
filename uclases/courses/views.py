from itertools import chain
from operator import attrgetter

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from .models import OfertaClase, SolicitudClase, HorarioOfertado, Inscripcion
from .enums import DiaSemana
from .forms import HorarioFormSet, OfertaForm, SolicitudClaseForm
from .services.inscription_service import InscriptionService


def publications_view(request):
    """
    Lista todas las publicaciones (ofertas y solicitudes de clases) ordenadas por fecha.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
    
    Returns:
        HttpResponse: Renderiza la lista completa de publicaciones combinadas y ordenadas.
    
    Template:
        'courses/publications_list.html'
    
    Dependencies:
        - courses.models (OfertaClase, SolicitudClase)
        - itertools.chain, operator.attrgetter
    """
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
    """
    Muestra el detalle completo de una oferta de clase con sus horarios ordenados.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
        pk (int): Clave primaria de la oferta a visualizar.
    
    Returns:
        HttpResponse: Renderiza la vista detallada de la oferta con horarios ordenados por día y hora.
    
    Template:
        'courses/oferta_detail.html'
    
    Dependencies:
        - courses.models.OfertaClase
        - courses.enums.DiaSemana
    """
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
    """
    Muestra el detalle completo de una solicitud de clase.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
        pk (int): Clave primaria de la solicitud a visualizar.
    
    Returns:
        HttpResponse: Renderiza la vista detallada de la solicitud.
    
    Template:
        'courses/solicitud_detail.html'
    
    Dependencies:
        - courses.models.SolicitudClase
    """
    solicitud = get_object_or_404(SolicitudClase, pk=pk)
    
    context = {
        'solicitud': solicitud,
    }
    return render(request, 'courses/solicitud_detail.html', context)

@login_required
def crear_oferta(request):
    """
    Permite a un usuario autenticado crear una nueva oferta de clase con horarios asociados.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP con datos del formulario y formset en POST.
    
    Returns:
        HttpResponse: Renderiza el formulario de creación en GET.
        HttpResponseRedirect: Redirige al detalle de la oferta tras creación exitosa.
    
    Template:
        'courses/crear_oferta.html'
    
    Dependencies:
        - courses.forms (OfertaForm, HorarioFormSet)
        - django.contrib.auth.decorators.login_required
    """
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
    """
    Permite a un usuario autenticado crear una nueva solicitud de clase.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP con datos del formulario en POST.
    
    Returns:
        HttpResponse: Renderiza el formulario de creación en GET.
        HttpResponseRedirect: Redirige al detalle de la solicitud tras creación exitosa.
    
    Template:
        'courses/crear_solicitud.html'
    
    Dependencies:
        - courses.forms.SolicitudClaseForm
        - django.contrib.auth.decorators.login_required
    """
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
    """
    Permite al creador de una oferta editarla junto con sus horarios asociados.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP con datos del formulario en POST.
        pk (int): Clave primaria de la oferta a editar.
    
    Returns:
        HttpResponse: Renderiza el formulario de edición con datos actuales.
        HttpResponseRedirect: Redirige al detalle tras actualización exitosa o si no tiene permisos.
    
    Template:
        'courses/editar_oferta.html'
    
    Dependencies:
        - courses.forms (OfertaForm, HorarioFormSet)
        - courses.models.OfertaClase
        - django.contrib.auth.decorators.login_required
    """
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
    """
    Permite al creador de una solicitud editarla.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP con datos del formulario en POST.
        pk (int): Clave primaria de la solicitud a editar.
    
    Returns:
        HttpResponse: Renderiza el formulario de edición con datos actuales.
        HttpResponseRedirect: Redirige al detalle tras actualización exitosa o si no tiene permisos.
    
    Template:
        'courses/editar_solicitud.html'
    
    Dependencies:
        - courses.forms.SolicitudClaseForm
        - courses.models.SolicitudClase
        - django.contrib.auth.decorators.login_required
    """
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
    """
    Permite a un estudiante seleccionar un horario específico e inscribirse en una oferta de clase.
    
    GET: Muestra un formulario con los horarios disponibles de la oferta ordenados por día y hora.
    POST: Procesa la inscripción del estudiante en el horario seleccionado.
    
    Validaciones realizadas:
        - Verifica que haya cupos disponibles en el horario seleccionado
        - Cuenta inscripciones activas (estados: Pendiente y Aceptado)
        - Previene inscripciones duplicadas en el mismo horario
        - Reduce automáticamente el número de cupos al inscribirse exitosamente
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP con horario_id en POST.
        pk (int): ID de la oferta de clase en la que se desea inscribir.
        
    Returns:
        HttpResponse: Renderiza el template con formulario de selección de horarios en GET.
        HttpResponseRedirect: Redirige al detalle de la oferta tras procesar la inscripción.
    
    Template:
        'courses/inscribirse.html'
    
    Dependencies:
        - courses.models.OfertaClase
        - courses.models.HorarioOfertado
        - courses.models.Inscripcion
    """
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
            # La inscripción se crea en estado PENDIENTE
            # Los cupos solo se reducirán cuando el profesor acepte la inscripción
            messages.success(request, "¡Inscripción enviada! El profesor debe aceptarla.")

        return redirect("courses:oferta_detail", pk=oferta.pk)

    context = {
        "oferta": oferta,
        "horarios_ordenados": horarios_ordenados,
    }
    return render(request, "courses/inscribirse.html", context)


@login_required
def aceptar_inscripcion(request, pk):
    """
    Permite al profesor aceptar una inscripción pendiente desde notificaciones.
    
    Delega la lógica al InscriptionService para mantener SRP.
    El servicio maneja: validaciones, cambio de estado, cupos y notificaciones.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP (requiere POST).
        pk (int): ID de la inscripción a aceptar.
    
    Returns:
        HttpResponseRedirect: Redirige a la lista de notificaciones.
    """
    inscripcion = get_object_or_404(Inscripcion, pk=pk)
    
    if request.method == "POST":
        # Usar el servicio para manejar la lógica
        success, message = InscriptionService.accept_inscription(
            inscription=inscripcion,
            user=request.user
        )
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
    
    return redirect('notifications:list')


@login_required
def rechazar_inscripcion(request, pk):
    """
    Permite al profesor rechazar una inscripción pendiente desde notificaciones.
    
    Delega la lógica al InscriptionService para mantener SRP.
    El servicio maneja: validaciones, cambio de estado y notificaciones.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP (requiere POST).
        pk (int): ID de la inscripción a rechazar.
    
    Returns:
        HttpResponseRedirect: Redirige a la lista de notificaciones.
    """
    inscripcion = get_object_or_404(Inscripcion, pk=pk)
    
    if request.method == "POST":
        # Usar el servicio para manejar la lógica
        success, message = InscriptionService.reject_inscription(
            inscription=inscripcion,
            user=request.user
        )
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
    
    return redirect('notifications:list')


@login_required
def cancelar_inscripcion(request, pk):
    """
    Permite al estudiante cancelar su propia inscripción desde notificaciones.
    
    Delega la lógica al InscriptionService para mantener SRP.
    El servicio maneja: validaciones, cambio de estado, cupos y notificaciones.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP (requiere POST).
        pk (int): ID de la inscripción a cancelar.
    
    Returns:
        HttpResponseRedirect: Redirige a la lista de notificaciones.
    """
    inscripcion = get_object_or_404(Inscripcion, pk=pk)
    
    if request.method == "POST":
        # Usar el servicio para manejar la lógica
        success, message = InscriptionService.cancel_inscription(
            inscription=inscripcion,
            user=request.user
        )
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
    
    return redirect('notifications:list')