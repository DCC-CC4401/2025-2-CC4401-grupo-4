from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm, PasswordResetForm
from django.conf import settings
from django.core.validators import validate_email
from .models import User, Perfil

INPUT_CLASS = "appearance-none my-4 w-full px-4 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary transition"
TEXTAREA_CLASS = "mt-4 w-full px-4 py-3 border border-border rounded-xl outline-hidden bg-card text-foreground placeholder:text-muted-foreground transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"

class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': INPUT_CLASS})
        self.fields['email'].widget.attrs.update({'class': INPUT_CLASS})
        self.fields['password1'].widget.attrs.update({'class': INPUT_CLASS})
        self.fields['password2'].widget.attrs.update({'class': INPUT_CLASS})

    def clean_email(self):
        email = self.cleaned_data.get("email").strip()
        if email is None:
            raise forms.ValidationError("El correo electrónico es obligatorio.")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ese email ya está registrado.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get("username").strip()
        if username is None:
            raise forms.ValidationError("El nombre de usuario es obligatorio.")
        if len(username) < 4:
            raise forms.ValidationError("El nombre de usuario debe tener al menos 4 caracteres.")
        if len(username) > 20:
            raise forms.ValidationError("El nombre de usuario no puede tener más de 20 caracteres.")
        if not all(c.isalnum() or c == "_" for c in username):
            raise forms.ValidationError("El nombre de usuario solo puede contener letras, números y guiones bajos.")
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Ese nombre de usuario ya está en uso.")
        return username
    
    


class CustomLoginForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': INPUT_CLASS, 'autofocus': True})
        self.fields['password'].widget.attrs.update({'class': INPUT_CLASS})
    def clean_username(self):
        username = self.cleaned_data.get("username").strip()
        if username is None:
            raise forms.ValidationError("El nombre de usuario o correo electrónico es obligatorio.")
        # Allowing login with email in username field
        if '@' in username:
            try:
                validate_email(username)
                user = User.objects.get(email__iexact=username)
                return user.username
            except User.DoesNotExist:
                raise forms.ValidationError("No existe una cuenta con ese correo electrónico.")
            except forms.ValidationError:
                raise forms.ValidationError("Ingresa un correo electrónico válido.")
        # Non email username validation
        else:
            if not User.objects.filter(username__iexact=username).exists():
                raise forms.ValidationError("No existe una cuenta con ese nombre de usuario.")
        return User.objects.filter(username__iexact=username).first()
    def clean_password(self):
        password = self.cleaned_data.get("password").strip()
        if password is None:
            raise forms.ValidationError("La contraseña es obligatoria.")
        return password

class CustomSetPasswordForm(SetPasswordForm):

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        f = self.fields
        f['new_password1'].widget.attrs.update({'class': INPUT_CLASS, 'placeholder': 'Ingresa tu nueva contraseña'})
        f['new_password2'].widget.attrs.update({'class': INPUT_CLASS, 'placeholder': 'Confirma tu nueva contraseña'})

class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.fields['email'].label = "Correo electrónico"
        self.fields['email'].widget.attrs.update({'class': INPUT_CLASS, 'placeholder': 'tucorreo@dominio.com', 'autocomplete': 'email'})


## FORMULARIO DE EDICIÓN DE USUARIO
class UserForm(forms.ModelForm):
    """Formulario para editar datos del modelo User,
    tiene username, first_name, last_name y email.
    """
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': INPUT_CLASS, 
                'placeholder': 'Nombre de usuario'
            }),
            'first_name': forms.TextInput(attrs={
                'class': INPUT_CLASS, 
                'placeholder': 'Nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': INPUT_CLASS, 
                'placeholder': 'Apellido'
            }),
            'email': forms.EmailInput(attrs={
                'class': INPUT_CLASS, 
                'placeholder': 'tucorreo@dominio.com'
            }),
        }
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico'
        }
    
    def clean_username(self):
        """Validar que el username no esté en uso por otro usuario"""
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ese nombre de usuario ya está en uso.")
        return username
    
    def clean_email(self):
        """Validar que el email no esté en uso por otro usuario"""
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ese email ya está registrado por otro usuario.")
        return email


# ============================================
# FORMULARIOS DE EDICIÓN DE PERFIL
# ============================================

class ProfileForm(forms.ModelForm):
    """Formulario para editar datos del modelo Perfil"""
    class Meta:
        model = Perfil
        fields = ['telefono', 'descripcion', 'foto_url', 'banner_url', 'carrera', 'ramos_cursados']
        widgets = {
            'telefono': forms.TextInput(attrs={
                'class': INPUT_CLASS, 
                'placeholder': '+56912345678'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': TEXTAREA_CLASS,
                'placeholder': 'Cuéntanos sobre ti...',
                'rows': 4
            }),
            'foto_url': forms.URLInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'https://ejemplo.com/foto.jpg'
            }),
            'banner_url': forms.URLInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'https://ejemplo.com/banner.jpg'
            }),
            'carrera': forms.Select(attrs={
                'class': INPUT_CLASS
            }),
            'ramos_cursados': forms.CheckboxSelectMultiple()
        }
        labels = {
            'telefono': 'Teléfono',
            'descripcion': 'Descripción',
            'foto_url': 'URL de foto de perfil',
            'banner_url': 'URL de banner',
            'carrera': 'Carrera',
            'ramos_cursados': 'Ramos cursados'
        }

class DescriptionForm(forms.ModelForm):
    """Formulario para editar SOLO la descripción"""
    class Meta:
        model = Perfil
        fields = ['descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={
                'class': TEXTAREA_CLASS,
                'placeholder': 'Cuéntanos sobre ti...',
                'rows': 5
            })
        }

class ImagesForm(forms.ModelForm):
    """Formulario para editar SOLO las imágenes"""
    class Meta:
        model = Perfil
        fields = ['foto_url', 'banner_url', 'foto_file', 'banner_file']
        widgets = {
            'foto_url': forms.URLInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'https://ejemplo.com/foto.jpg'
            }),
            'banner_url': forms.URLInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'https://ejemplo.com/banner.jpg'
            }),
            'foto_file': forms.ClearableFileInput(attrs={
                'class': INPUT_CLASS, 'accept': 'image/*'
            }),
            'banner_file': forms.ClearableFileInput(attrs={
                'class': INPUT_CLASS, 'accept': 'image/*'
            }),
        }
        labels = {
            'foto_url': 'URL de foto de perfil',
            'banner_url': 'URL de banner',
            'foto_file': 'Subir foto de perfil',
            'banner_file': 'Subir banner'
        }

class CareerForm(forms.ModelForm):
    """Formulario para editar SOLO carrera y ramos"""
    class Meta:
        model = Perfil
        fields = ['carrera', 'ramos_cursados']
        widgets = {
            'carrera': forms.Select(attrs={'class': INPUT_CLASS}),
            'ramos_cursados': forms.SelectMultiple(attrs={'class': INPUT_CLASS})
        }
        labels = {
            'carrera': 'Carrera actual',
            'ramos_cursados': 'Agregar ramos cursados'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si hay una instancia (perfil existente), filtrar los ramos ya cursados
        if self.instance and self.instance.pk:
            from courses.models import Ramo
            ramos_ya_cursados = self.instance.ramos_cursados.all()
            # Mostrar solo los ramos que NO están ya seleccionados
            self.fields['ramos_cursados'].queryset = Ramo.objects.exclude(
                id__in=ramos_ya_cursados.values_list('id', flat=True)
            )
            # Cambiar a required=False para permitir no seleccionar nada
            self.fields['ramos_cursados'].required = False
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            # AÑADIR los nuevos ramos seleccionados a los existentes
            nuevos_ramos = self.cleaned_data.get('ramos_cursados')
            if nuevos_ramos:
                for ramo in nuevos_ramos:
                    instance.ramos_cursados.add(ramo)
        return instance

class PerfilRamoForm(forms.ModelForm):
    """Formulario para editar SOLO ramos cursados"""
    class Meta:
        model = Perfil
        fields = ['ramos_cursados']
        widgets = {
            'ramos_cursados': forms.SelectMultiple(attrs={'class': INPUT_CLASS})
        }
        labels = {
            'ramos_cursados': 'Ramos cursados'
        }
        
class ContactInfoForm(forms.ModelForm):
    """Formulario para editar SOLO teléfono"""
    class Meta:
        model = Perfil
        fields = ['telefono']
        widgets = {
            'telefono': forms.TextInput(attrs={
                'class': INPUT_CLASS, 
                'placeholder': '+56912345678'
            })
        }
        labels = {'telefono': 'Teléfono'}