from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

from .forms import (
    CustomLoginForm,
    SignUpForm,
    ProfileForm,
    DescriptionForm,
    ImagesForm,
    CareerForm,
    ContactInfoForm,
)
from .models import User

@login_required
def logout_view(request):
    """
    Cierra la sesión del usuario autenticado y redirige a la página principal.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP con el usuario autenticado.
    
    Returns:
        HttpResponseRedirect: Redirige a la vista 'home' después de cerrar sesión.
    
    Dependencies:
        - django.contrib.auth.logout
        - django.contrib.auth.decorators.login_required
    """
    logout(request)
    messages.success(request, 'Sesion cerrada correctamente.')
    return redirect('home')


def signin_view(request):
    """
    Maneja el inicio de sesión de usuarios mediante formulario personalizado.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP con credenciales de usuario en POST.
    
    Returns:
        HttpResponse: Renderiza el formulario de login en GET.
        HttpResponseRedirect: Redirige a 'home' si las credenciales son válidas.
    
    Template:
        'accounts/login.html'
    
    Dependencies:
        - accounts.forms.CustomLoginForm
        - django.contrib.auth.login
    """
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bienvenido de nuevo {user.username}!')
            return redirect('home')
        else:
            messages.error(
                request, 'No pudimos iniciar sesion. Revisa la informacion e intenta de nuevo.')
    else:
        form = CustomLoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


def signup_view(request):
    """
    Registra un nuevo usuario y lo autentica automáticamente al completar el registro.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP con datos del formulario en POST.
    
    Returns:
        HttpResponse: Renderiza el formulario de registro en GET.
        HttpResponseRedirect: Redirige a 'home' tras registro exitoso e inicio de sesión automático.
    
    Template:
        'accounts/signup.html'
    
    Dependencies:
        - accounts.forms.SignUpForm
        - django.contrib.auth.login
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registro completado, sesion iniciada.')
            return redirect('home')
        else:
            messages.error(
                request, 'Revisa la informacion y vuelve a intentarlo.')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def felmer_view(request):
    """
    Vista de felmer, es un easter egg(goat).
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
    
    Returns:
        HttpResponse: Renderiza la plantilla 'profile/felmer.html'.
    
    Template:
        'profile/felmer.html'
    """
    return render(request, 'profile/felmer.html')

def my_profile_view(request):
    """
    Muestra y permite editar el perfil del usuario autenticado con múltiples formularios.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP con datos de usuario y formularios en POST.
    
    Returns:
        HttpResponse: Renderiza el perfil editable con todos los formularios.
        HttpResponseRedirect: Redirige tras actualización exitosa o si no está autenticado te lleva al login.
    
    Template:
        'profile/my_profile.html'
    
    Dependencies:
        - accounts.forms (DescriptionForm, ImagesForm, CareerForm, ContactInfoForm, ProfileForm)
        - accounts.models.Perfil
    """
    if not request.user.is_authenticated:
        messages.error(request, 'Debes iniciar sesión para ver tu perfil.')
        return redirect('accounts:login')

    user = request.user
    perfil = user.perfil
    
    # Obtener ramos únicos de ofertas (sin duplicados)
    ramos_dictados = set()
    for oferta in perfil.ofertas_creadas.all():
        if oferta.ramo:  # Ahora ramo es ForeignKey (un solo ramo)
            ramos_dictados.add(oferta.ramo)
    
    # Obtener ramos únicos de solicitudes (sin duplicados)
    ramos_solicitados = set()
    for solicitud in perfil.solicitudes_creadas.all():
        if solicitud.ramo:
            ramos_solicitados.add(solicitud.ramo)

    target_prefix = request.POST.get("form_prefix") if request.method == "POST" else None

    description_form = DescriptionForm(
        request.POST if target_prefix == "desc" else None,
        instance=perfil,
        prefix="desc",
    )
    images_form = ImagesForm(
        request.POST if target_prefix == "img" else None,
        request.FILES if target_prefix == "img" else None,
        instance=perfil,
        prefix="img",
    )
    career_form = CareerForm(
        request.POST if target_prefix == "career" else None,
        instance=perfil,
        prefix="career",
    )
    contact_form = ContactInfoForm(
        request.POST if target_prefix == "contact" else None,
        instance=perfil,
        prefix="contact",
    )
    profile_form = ProfileForm(
        request.POST if target_prefix == "main" else None,
        instance=perfil,
        prefix="main",
    )

    forms_map = {
        "desc": description_form,
        "img": images_form,
        "career": career_form,
        "contact": contact_form,
        "main": profile_form,
    }

    if request.method == "POST":
        selected_form = forms_map.get(target_prefix)
        if selected_form and selected_form.is_valid():
            selected_form.save()
            messages.success(request, "Tu perfil se ha actualizado correctamente.")
            return redirect('accounts:my_profile')
        messages.error(request, "Reingresa la informacion y vuelve a intentarlo.")

    context = {
        'profile_user': user,
        'perfil': perfil,
        'description_form': description_form,
        'images_form': images_form,
        'career_form': career_form,
        'contact_info_form': contact_form,
        'profile_form': profile_form,
        'ramos_dictados': sorted(ramos_dictados, key=lambda r: r.name),
        'ramos_solicitados': sorted(ramos_solicitados, key=lambda r: r.name),
        'share_url': request.build_absolute_uri(
            reverse('accounts:profile_detail', args=[user.public_uid])
        ),
        #aqui se añaden los forms en caso de que se quiera editar
    }

    return render(request, 'profile/my_profile.html', context)

# only lecture

def profile_detail_view(request, public_uid):
    """
    Muestra el perfil público de un usuario identificado por su UUID público.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
        public_uid (UUID): Identificador público único del usuario a visualizar.
    
    Returns:
        HttpResponse: Renderiza el perfil público del usuario.
        HttpResponseRedirect: Redirige a 'my_profile' si el usuario visita su propio perfil con su uid.
    
    Template:
        'profile/profile_detail_view.html'
    
    Dependencies:
        - accounts.models.User
        - django.shortcuts.get_object_or_404
    """
    from courses.models import Inscripcion, Rating
    from courses.enums import EstadoInscripcion
    from courses.forms import RatingForm
    
    user = get_object_or_404(User, public_uid=public_uid)
    
    # Redirigir a mi perfil si es el usuario autenticado
    if request.user.is_authenticated and request.user == user:
        return redirect('accounts:my_profile')
    
    perfil = user.perfil
    
    # Obtener ramos únicos de ofertas (sin duplicados)
    ramos_dictados = set()
    for oferta in perfil.ofertas_creadas.all():
        if oferta.ramo:  # Ahora ramo es ForeignKey (un solo ramo)
            ramos_dictados.add(oferta.ramo)
    
    # Obtener ramos únicos de solicitudes (sin duplicados)
    ramos_solicitados = set()
    for solicitud in perfil.solicitudes_creadas.all():
        if solicitud.ramo:
            ramos_solicitados.add(solicitud.ramo)
    
    # Verificar si el usuario actual puede dejar un rating
    can_rate = False
    completed_inscriptions = []
    rating_form = None
    
    if request.user.is_authenticated:
        # Buscar inscripciones completadas del usuario actual con este profesor
        completed_inscriptions = Inscripcion.objects.filter(
            estudiante=request.user.perfil,
            horario_ofertado__oferta__profesor=perfil,
            estado=EstadoInscripcion.COMPLETADO
        ).select_related('horario_ofertado__oferta')
        
        # Verificar si alguna inscripción completada NO tiene rating
        for inscripcion in completed_inscriptions:
            if not Rating.objects.filter(inscripcion=inscripcion).exists():
                can_rate = True
                rating_form = RatingForm()
                break

    context = {
        'profile_user': user,
        'perfil': perfil,
        'ramos_dictados': sorted(ramos_dictados, key=lambda r: r.name),
        'ramos_solicitados': sorted(ramos_solicitados, key=lambda r: r.name),
        'share_url': request.build_absolute_uri(
            reverse('accounts:profile_detail', args=[user.public_uid])
        ),
        'can_rate': can_rate,
        'rating_form': rating_form,
        'completed_inscriptions': completed_inscriptions,
    }

    return render(request, 'profile/profile_detail_view.html', context)