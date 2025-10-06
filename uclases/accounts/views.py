from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomLoginForm, SignUpForm, ProfileForm
from .models import Perfil, User
from courses.models import Carrera
from django.shortcuts import get_object_or_404
from django.conf import settings
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

    context = {
        'profile_user': user,
        'perfil': perfil,
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
