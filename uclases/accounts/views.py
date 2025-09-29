from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomLoginForm , SignUpForm
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
            messages.error(request, 'No pudimos iniciar sesion. Revisa la informacion e intenta de nuevo.')
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
            messages.error(request, 'Revisa la informacion y vuelve a intentarlo.')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})
