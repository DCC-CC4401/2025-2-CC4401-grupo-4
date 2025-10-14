from itertools import chain
from operator import attrgetter

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from .models import OfertaClase, SolicitudClase
from .enums import DiaSemana
from .forms import HorarioFormSet, OfertaForm, SolicitudClaseForm


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