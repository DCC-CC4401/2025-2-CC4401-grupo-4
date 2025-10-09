from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import (
    CustomLoginForm,
    SignUpForm,
    ProfileForm,
    DescriptionForm,
    ImagesForm,
    CareerForm,
    ContactInfoForm,
)
from .models import Perfil, User
from courses.models import Carrera
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.urls import reverse
# Create your views here.


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Sesion cerrada correctamente.')
    return redirect('home')


def signin_view(request):
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
    return render(request, 'profile/felmer.html')

# editable profile
def my_profile_view(request):
    """Vista del perfil del usuario autenticado"""
    if not request.user.is_authenticated:
        messages.error(request, 'Debes iniciar sesión para ver tu perfil.')
        return redirect('accounts:login')

    user = request.user
    perfil = user.perfil

     # Obtener ramos únicos de ofertas (sin duplicados)
    ramos_dictados = set()
    for oferta in perfil.ofertas_creadas.all():
        for ramo in oferta.ramos.all():
            ramos_dictados.add(ramo)
    
    # Obtener ramos únicos de solicitudes (sin duplicados)
    ramos_solicitados = set()
    for solicitud in perfil.solicitudes_creadas.all():
        ramos_solicitados.add(solicitud.ramo)

    target_prefix = request.POST.get("form_prefix") if request.method == "POST" else None

    description_form = DescriptionForm(
        request.POST if target_prefix == "desc" else None,
        instance=perfil,
        prefix="desc",
    )
    images_form = ImagesForm(
        request.POST if target_prefix == "img" else None,
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
    """Vista del perfil público de un usuario usando su UUID"""
    user = get_object_or_404(User, public_uid=public_uid)
    perfil = user.perfil

    context = {
        'profile_user': user,
        'perfil': perfil,
    }

    return render(request, 'profile/profile_detail_view.html', context)