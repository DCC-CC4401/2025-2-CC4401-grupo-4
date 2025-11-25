from itertools import chain
from operator import attrgetter

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from .models import OfertaClase, SolicitudClase, HorarioOfertado, Inscripcion, Ramo ,Rating
from accounts.models import Perfil
from .enums import DiaSemana , EstadoInscripcion
from .forms import HorarioFormSet, OfertaForm, SolicitudClaseForm,  ComentarioForm, RatingForm
from .services.inscription_service import InscriptionService
from notifications.services.notification_service import NotificationService
from notifications.enums import NotificationTypes



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
    if request.method == "POST":
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.oferta_clase = oferta
            comentario.publicador = request.user.perfil
            comentario.save()
            messages.success(request, "Comentario agregado correctamente.")
            return redirect('courses:oferta_detail', pk=oferta.pk)
    else:
        form = ComentarioForm()

    context = {
        'oferta': oferta,
        'horarios_ordenados': horarios_ordenados,
        'dias_semana': DiaSemana,
        'comentario_form': form,
        'comentarios': oferta.comentarios.all()
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

    puede_proponer_clase = False
    if request.user.is_authenticated:
        if request.user.perfil.ramos_cursados.filter(pk=solicitud.ramo.pk).exists():
             puede_proponer_clase = True
    if request.method == "POST":
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.solicitud_clase = solicitud
            comentario.publicador = request.user.perfil
            comentario.save()
            messages.success(request, "Comentario agregado correctamente.")
            return redirect('courses:solicitud_detail', pk=solicitud.pk)
    else:
        form = ComentarioForm()
    
    context = {
        'solicitud': solicitud,
        'comentario_form': form,
        'comentarios': solicitud.comentarios.all(),
        'puede_proponer_clase': puede_proponer_clase,
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
    
    # Obtener todos los horarios ordenados
    horarios_ordenados = oferta.horarios.all().order_by('dia', 'hora_inicio')
    
    # Obtener inscripciones del usuario en esta oferta con su estado
    inscripciones_usuario = Inscripcion.objects.filter(
        estudiante=request.user.perfil,
        horario_ofertado__oferta=oferta,
        estado__in=[EstadoInscripcion.PENDIENTE, EstadoInscripcion.ACEPTADO, EstadoInscripcion.COMPLETADO]
    ).select_related('horario_ofertado')
    
    # Crear diccionario de horario_id -> inscripción
    inscripciones_dict = {ins.horario_ofertado_id: ins for ins in inscripciones_usuario}
    
    # Anotar cada horario con el estado de inscripción del usuario
    for horario in horarios_ordenados:
        if horario.id in inscripciones_dict:
            horario.usuario_inscrito = True
            horario.inscripcion_estado = inscripciones_dict[horario.id].estado
            horario.inscripcion_estado_display = inscripciones_dict[horario.id].get_estado_display()
        else:
            horario.usuario_inscrito = False
            horario.inscripcion_estado = None

    # Determinar si existe al menos un horario con cupos disponibles
    has_available = any((not h.usuario_inscrito) and (h.cupos_totales > 0) for h in horarios_ordenados)

    if request.method == "POST":
        horario_id = request.POST.get("horario")
        
        # Validar que se haya seleccionado un horario
        if not horario_id:
            messages.error(request, "Debes seleccionar un horario válido.")
            return redirect("courses:inscribirse", pk=oferta.pk)
        
        # Validar que el horario existe y pertenece a esta oferta
        try:
            horario = HorarioOfertado.objects.get(id=horario_id, oferta=oferta)
        except HorarioOfertado.DoesNotExist:
            messages.error(request, "El horario seleccionado no es válido.")
            return redirect("courses:inscribirse", pk=oferta.pk)
        
        # Verificar si el usuario ya está inscrito en este horario
        inscripcion_existente = Inscripcion.objects.filter(
            estudiante=request.user.perfil,
            horario_ofertado=horario,
            estado__in=[EstadoInscripcion.PENDIENTE, EstadoInscripcion.ACEPTADO, EstadoInscripcion.COMPLETADO]
        ).exists()
        
        if inscripcion_existente:
            messages.warning(request, "Ya estás inscrito en este horario.")
            return redirect("courses:inscribirse", pk=oferta.pk)

        # Verificar cupos
        inscripciones_activas = horario.inscripciones.filter(
            estado__in=[0, 1]  # Pendiente o Aceptado
        ).count()

        if inscripciones_activas >= horario.cupos_totales:
            messages.error(request, "Lo sentimos, este horario ya no tiene cupos disponibles.")
            return redirect("courses:inscribirse", pk=oferta.pk)

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
        "has_available": has_available,
    }
    return render(request, "courses/inscribirse.html", context)


@login_required
def aceptar_inscripcion(request, pk):
    """
    Permite al profesor aceptar una inscripción pendiente.
    
    Delega la lógica al InscriptionService para mantener SRP.
    El servicio maneja: validaciones, cambio de estado, cupos y notificaciones.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP (requiere POST).
        pk (int): ID de la inscripción a aceptar.
    
    Returns:
        HttpResponseRedirect: Redirige a la página anterior o a mis inscripciones.
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
    
    # Redirigir a la página anterior o a mis inscripciones
    next_url = request.GET.get('next') or request.POST.get('next') or 'courses:mis_inscripciones'
    return redirect(next_url)


@login_required
def rechazar_inscripcion(request, pk):
    """
    Permite al profesor rechazar una inscripción pendiente.
    
    Delega la lógica al InscriptionService para mantener SRP.
    El servicio maneja: validaciones, cambio de estado y notificaciones.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP (requiere POST).
        pk (int): ID de la inscripción a rechazar.
    
    Returns:
        HttpResponseRedirect: Redirige a la página anterior o a mis inscripciones.
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
    
    # Redirigir a la página anterior o a mis inscripciones
    next_url = request.GET.get('next') or request.POST.get('next') or 'courses:mis_inscripciones'
    return redirect(next_url)


@login_required
def cancelar_inscripcion(request, pk):
    """
    Permite al estudiante cancelar su propia inscripción.
    
    Delega la lógica al InscriptionService para mantener SRP.
    El servicio maneja: validaciones, cambio de estado, cupos y notificaciones.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP (requiere POST).
        pk (int): ID de la inscripción a cancelar.
    
    Returns:
        HttpResponseRedirect: Redirige a la página anterior o a mis inscripciones.
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
    # Redirigir a la página anterior o a mis inscripciones
    next_url = request.GET.get('next') or request.POST.get('next') or 'courses:mis_inscripciones'
    return redirect(next_url)

@login_required
def proponer_oferta_clase(request, solicitud_id):
    """
    Permite a un profesor crear y enviar una OfertaClase privada en respuesta
    a una SolicitudClase específica. La oferta queda automáticamente vinculada
    al Ramo de la solicitud y marcada como 'privada'.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP. Contiene los datos del
                               OfertaForm y HorarioFormSet en el método POST.
        solicitud_id (int): ID de la SolicitudClase a la que se está respondiendo.
    
    Returns:
        HttpResponse: Renderiza el formulario de propuesta de clase.
        HttpResponseRedirect: 
            1. Redirige al detalle de la Solicitud (almacenamiento exitoso).
            2. Redirige a la lista de solicitudes (si el profesor es el mismo solicitante).
    
    Template:
        'courses/proponer_oferta.html'
    
    Dependencies:
        - courses.forms.OfertaForm
        - courses.forms.HorarioFormSet (inline formset)
        - courses.models.SolicitudClase
        - courses.models.OfertaClase
        - django.contrib.auth.decorators.login_required
    """
    
    solicitud = get_object_or_404(SolicitudClase, id=solicitud_id)
    ramo = solicitud.ramo
    solicitante_perfil = solicitud.solicitante
    profesor_perfil = request.user.perfil
    
    if profesor_perfil.user.id == solicitante_perfil.user.id:
        messages.error(request, 'No puedes proponer una clase a tu propia solicitud. Usa el botón de editar.')
        return redirect('courses:solicitud_detail', solicitud_id) 
    
    if not request.user.perfil.ramos_cursados.filter(pk=ramo.pk).exists():
        messages.error(request, f'No tienes permiso para proponer clases de {ramo.name}.')
        return redirect('courses:solicitud_detail', solicitud_id)
    
    if request.method == 'POST':
        form = OfertaForm(request.POST, user=request.user)
        formset = HorarioFormSet(request.POST) 
        if form.is_valid() and formset.is_valid():
            oferta = form.save(commit=False)
            oferta.profesor = profesor_perfil
            
            oferta.ramo = ramo

            oferta.public = False

            oferta.save()
            
            formset.instance = oferta 
            formset.save()
            # Intentar enviar notificación al solicitante (si el módulo notifications está disponible)
            

            NotificationService.send(
                receiver=solicitante_perfil,
                type=NotificationTypes.OFERTA_PROPOSED,
                data={'oferta': oferta},
                related_object=oferta
            )


            messages.success(request, f'Tu oferta de clase de {ramo.name} ha sido publicada y el solicitante ha sido notificado.')
            
            return redirect('courses:solicitud_detail', solicitud_id) 

    else:

        initial_data = {
            'ramo': ramo.id,
            'titulo': f'Clase propuesta: {ramo.name}', 
            'descripcion': f'Propuesta en respuesta a la solicitud de {solicitante_perfil.user.username}.',
        }
        
        form = OfertaForm(initial=initial_data, user=request.user) 
        formset = HorarioFormSet()
        
        form.fields['ramo'].initial = ramo
        form.fields['ramo'].widget.attrs['disabled'] = 'disabled'
        form.fields['ramo'].widget.attrs['class'] += ' opacity-50 cursor-not-allowed'
        
    context = {
        'form': form,
        'formset': formset,
        'ramo': ramo,
        'solicitante': solicitante_perfil,
    }
    return render(request, 'courses/proponer_oferta.html', context)
   


@login_required
def mis_inscripciones_view(request):
    """
    Vista de gestión de inscripciones.
    
    Para profesores: Muestra inscripciones a sus ofertas de clase con opción de aceptar/rechazar.
    Para estudiantes: Muestra sus propias inscripciones con opción de cancelar las pendientes.
    
    Incluye contadores por estado y filtrado client-side con JavaScript.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
    
    Returns:
        HttpResponse: Renderiza la vista de gestión con inscripciones filtradas según el rol.
    
    Template:
        'courses/mis_inscripciones.html'
    
    Dependencies:
        - courses.models.Inscripcion
        - courses.models.EstadoInscripcion
    """
    perfil = request.user.perfil
    
    # Obtener TODAS las inscripciones relevantes para el usuario
    # 1. Inscripciones a ofertas donde este perfil es el profesor
    inscripciones_como_profesor = Inscripcion.objects.filter(
        horario_ofertado__oferta__profesor=perfil
    ).select_related(
        'estudiante',
        'estudiante__user',
        'estudiante__carrera',
        'horario_ofertado__oferta__ramo'
    )
    
    # 2. Inscripciones propias donde este perfil es el estudiante
    inscripciones_como_estudiante = Inscripcion.objects.filter(
        estudiante=perfil
    ).select_related(
        'horario_ofertado__oferta__profesor',
        'horario_ofertado__oferta__profesor__user',
        'horario_ofertado__oferta__ramo'
    )
    
    # Combinar ambas querysets y eliminar duplicados
    inscripciones = (inscripciones_como_profesor | inscripciones_como_estudiante).distinct().order_by('-fecha_reserva')
    
    # Calcular contadores por estado
    all_count = inscripciones.count()
    pendiente_count = inscripciones.filter(estado=EstadoInscripcion.PENDIENTE).count()
    aceptado_count = inscripciones.filter(estado=EstadoInscripcion.ACEPTADO).count()
    rechazado_count = inscripciones.filter(estado=EstadoInscripcion.RECHAZADO).count()
    cancelado_count = inscripciones.filter(estado=EstadoInscripcion.CANCELADO).count()
    
    context = {
        'inscripciones': inscripciones,
        'EstadoInscripcion': EstadoInscripcion,
        'all_count': all_count,
        'pendiente_count': pendiente_count,
        'aceptado_count': aceptado_count,
        'rechazado_count': rechazado_count,
        'cancelado_count': cancelado_count,
    }
    
    return render(request, 'courses/mis_inscripciones.html', context)


@login_required
def dashboard_mis_ofertas(request):
    """
    Muestra un dashboard con las publicaciones (ofertas y solicitudes) creadas por el usuario autenticado.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
    
    Returns:
        HttpResponse: Renderiza la vista del dashboard con las publicaciones del usuario.
    
    Template:
        'courses/dashboard_mis_publicaciones.html'
    
    Dependencies:
        - courses.models.OfertaClase
        - courses.models.SolicitudClase
        - django.contrib.auth.decorators.login_required
    """
    perfil = request.user.perfil
    
    mis_ofertas = OfertaClase.objects.filter(profesor=perfil).order_by('-fecha_publicacion')
    
    
    context = {
        'mis_ofertas': mis_ofertas,
    }
    
    return render(request, 'courses/dashboard_ofertas.html', context)


@login_required
def mis_ofertas_horarios_view(request, oferta_id):
    """
    Muestra los horarios e inscritos de una oferta específica del profesor.
    
    Similar a mis_inscripciones_view pero filtrada solo por una oferta.
    Muestra todos los horarios de la oferta con inscripciones aceptadas y completadas.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
        oferta_id (int): ID de la oferta a visualizar.
    
    Returns:
        HttpResponse: Renderiza los horarios e inscritos de la oferta.
    
    Template:
        'courses/mis_ofertas_horarios.html'
    
    Dependencies:
        - courses.models.OfertaClase
        - courses.models.HorarioOfertado
        - courses.models.Inscripcion
    """
    perfil = request.user.perfil
    
    # Obtener la oferta verificando que pertenezca al profesor
    oferta = get_object_or_404(
        OfertaClase.objects.prefetch_related(
            'horarios__inscripciones__estudiante__user',
            'horarios__inscripciones__estudiante__carrera',
        ).select_related('ramo'),
        id=oferta_id,
        profesor=perfil
    )
    
    # Obtener todos los horarios de la oferta
    horarios = oferta.horarios.all().order_by('dia', 'hora_inicio')
    
    # Para cada horario, filtrar inscripciones por estado
    for horario in horarios:
        horario.inscritos_aceptados = horario.inscripciones.filter(
            estado=EstadoInscripcion.ACEPTADO
        ).select_related('estudiante__user', 'estudiante__carrera')
        horario.inscritos_completados = horario.inscripciones.filter(
            estado=EstadoInscripcion.COMPLETADO
        ).select_related('estudiante__user', 'estudiante__carrera')
    
    context = {
        'oferta': oferta,
        'horarios': horarios,
    }
    
    return render(request, 'courses/mis_ofertas_horarios.html', context)

@login_required
def dashboard_mis_solicitudes(request):
    """
    Muestra un dashboard con las publicaciones (ofertas y solicitudes) creadas por el usuario autenticado.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
    
    Returns:
        HttpResponse: Renderiza la vista del dashboard con las publicaciones del usuario.
    
    Template:
        'courses/dashboard_mis_publicaciones.html'
    
    Dependencies:
        - courses.models.OfertaClase
        - courses.models.SolicitudClase
        - django.contrib.auth.decorators.login_required
    """
    perfil = request.user.perfil
    
    mis_solicitudes = SolicitudClase.objects.filter(solicitante=perfil).order_by('-fecha_publicacion')
    
    
    context = {
        
        'mis_solicitudes': mis_solicitudes,
    }
    
    return render(request, 'courses/dashboard_solicitudes.html', context)



@login_required
def mis_horarios_view(request, id_oferta):
   
    perfil = request.user.perfil
    
    # Obtener ofertas del profesor con sus horarios e inscripciones
    ofertas = perfil.ofertas_creadas.prefetch_related(
        'horarios__inscripciones__estudiante__user',
        'horarios__inscripciones__estudiante__carrera',
        'ramo'
    ).all()
    
    # Para cada horario, contar inscripciones por estado
    for oferta in ofertas:
        for horario in oferta.horarios.all():
            horario.inscritos_aceptados = horario.inscripciones.filter(
                estado=EstadoInscripcion.ACEPTADO
            )
            horario.inscritos_completados = horario.inscripciones.filter(
                estado=EstadoInscripcion.COMPLETADO
            )
    
    context = {
        'ofertas': ofertas,
    }
    
    return render(request, 'courses/mis_clases.html', context)


@login_required
def completar_horario_view(request, pk):
    """
    Marca un horario como completado, actualizando todas las inscripciones
    aceptadas a estado COMPLETADO.

    Solo el profesor propietario de la oferta puede completar el horario.
    Notifica a todos los estudiantes afectados.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
        pk (int): ID del horario a completar.
    
    Returns:
        HttpResponse: Redirecciona a 'mis_clases' con mensaje de confirmación.
    
    Permissions:
        - Usuario autenticado
        - Ser el profesor de la oferta asociada al horario
    """
    horario = get_object_or_404(HorarioOfertado, pk=pk)
    
    # Validar que el usuario sea el profesor de la oferta
    if horario.oferta.profesor != request.user.perfil:
        messages.error(request, "No tienes permiso para completar este horario.")
        return redirect('courses:mis_clases')
    
    # Obtener inscripciones aceptadas para completar
    inscripciones_aceptadas = horario.inscripciones.filter(
        estado=EstadoInscripcion.ACEPTADO
    )
    
    if not inscripciones_aceptadas.exists():
        messages.warning(request, "No hay inscripciones aceptadas en este horario.")
        return redirect('courses:mis_clases')
    
    # Completar cada inscripción aceptada
    count = 0
    for inscripcion in inscripciones_aceptadas:
        inscripcion.completar()
        count += 1
    
    # Mensaje de confirmación
    dia = horario.get_dia_display()
    hora = f"{horario.hora_inicio.strftime('%H:%M')} - {horario.hora_fin.strftime('%H:%M')}"
    messages.success(
        request,
        f"Clase del {dia} ({hora}) marcada como completada. "
        f"{count} {'estudiante' if count == 1 else 'estudiantes'} {'notificado' if count == 1 else 'notificados'}."
    )
    
    # Redirigir a la vista de horarios de la oferta específica
    return redirect('courses:mis_ofertas_horarios', oferta_id=horario.oferta.id)


@login_required
def crear_rating_view(request):
    """
    Procesa la creación de un rating (valoración y comentario) para un profesor.
    
    Solo permite crear ratings si:
    - El usuario tiene una inscripción COMPLETADA con ese profesor
    - Aún no ha dejado un rating para esa clase
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP con datos POST del formulario.
    
    Returns:
        HttpResponseRedirect: Redirige al perfil del profesor con mensaje de éxito/error.
    
    Dependencies:
        - courses.forms.RatingForm
        - courses.models.Rating, Inscripcion
        - courses.enums.EstadoInscripcion
        - accounts.models.Perfil
    """
    if request.method != 'POST':
        messages.error(request, 'Método no permitido.')
        return redirect('home')
    
    profesor_id = request.POST.get('profesor_id')
    print(f"DEBUG - profesor_id recibido: {profesor_id}")
    print(f"DEBUG - POST data completo: {request.POST}")
    
    if not profesor_id:
        messages.error(request, f'Profesor no especificado. POST data: {dict(request.POST)}')
        return redirect('home')
    
    try:
        # Perfil usa user como primary key, entonces buscamos por user_id
        profesor = Perfil.objects.get(user_id=profesor_id)
        print(f"DEBUG - Profesor encontrado: {profesor.user.username}")
    except Perfil.DoesNotExist:
        messages.error(request, f'Profesor con ID {profesor_id} no encontrado.')
        return redirect('home')
    
    form = RatingForm(request.POST)
    
    if not form.is_valid():
        # Debug: mostrar errores específicos del formulario
        error_messages = []
        for field, errors in form.errors.items():
            error_messages.append(f"{field}: {', '.join(errors)}")
        messages.error(request, f'Formulario inválido: {"; ".join(error_messages)}')
        return redirect('accounts:profile_detail', public_uid=profesor.user.public_uid)
    
    # Buscar inscripciones completadas del usuario con este profesor
    inscripciones_completadas = Inscripcion.objects.filter(
        estudiante=request.user.perfil,
        horario_ofertado__oferta__profesor=profesor,
        estado=EstadoInscripcion.COMPLETADO
    ).select_related('horario_ofertado__oferta')
    
    if not inscripciones_completadas.exists():
        messages.error(request, 'No tienes clases completadas con este profesor.')
        return redirect('accounts:profile_detail', public_uid=profesor.user.public_uid)
    
    # Buscar la primera inscripción sin rating
    inscripcion_sin_rating = None
    for inscripcion in inscripciones_completadas:
        if not Rating.objects.filter(inscripcion=inscripcion).exists():
            inscripcion_sin_rating = inscripcion
            break
    
    if not inscripcion_sin_rating:
        messages.warning(request, 'Ya has calificado todas tus clases con este profesor.')
        return redirect('accounts:profile_detail', public_uid=profesor.user.public_uid)
    
    # Crear el rating
    rating = form.save(commit=False)
    rating.inscripcion = inscripcion_sin_rating
    rating.calificador = request.user.perfil
    rating.calificado = profesor  # El profesor siendo calificado
    rating.save()
    
    messages.success(request, f'¡Gracias por tu reseña! Has calificado con {rating.valoracion} estrellas.')
    return redirect('accounts:profile_detail', public_uid=profesor.user.public_uid)


@login_required
def eliminar_oferta(request, oferta_id):
    """
    Elimina una oferta de clase.
    
    La notificación a estudiantes inscritos se maneja automáticamente
    mediante el signal pre_delete en notifications.signals.offers_signals.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
        oferta_id (int): ID de la oferta a eliminar.
    
    Returns:
        HttpResponse: Redirecciona a la lista de ofertas del profesor.
    
    Business Logic:
        - Verifica que el usuario sea el profesor de la oferta
        - Elimina la oferta (el signal se encarga de notificar a estudiantes)
        - CASCADE eliminará horarios e inscripciones asociadas
    """
    oferta = get_object_or_404(OfertaClase, id=oferta_id, profesor=request.user.perfil)
    
    oferta_titulo = oferta.titulo
    oferta.delete()  # El signal pre_delete se encargará de las notificaciones
    
    messages.success(request, f"La oferta '{oferta_titulo}' ha sido eliminada correctamente.")
    return redirect('courses:mis_ofertas')