from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm, PasswordResetForm
from django.core.validators import validate_email
from .models import User, Perfil

INPUT_CLASS = "appearance-none my-4 w-full px-4 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary transition"
TEXTAREA_CLASS = "mt-4 w-full px-4 py-3 border border-border rounded-xl outline-hidden bg-card text-foreground placeholder:text-muted-foreground transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"

class SignUpForm(UserCreationForm):
    """
    Formulario de registro de nuevos usuarios.
    
    Extiende UserCreationForm de Django para incluir validaciones
    personalizadas de email y username. Valida unicidad de ambos campos
    y aplica restricciones de formato y longitud al nombre de usuario.
    
    Tipo: UserCreationForm (extiende)
    Modelo: accounts.models.User
    
    Campos:
        - username: Nombre de usuario (único, alfanumérico + guión bajo, 4-20 caracteres)
        - email: Correo electrónico único
        - password1: Contraseña
        - password2: Confirmación de contraseña
    """
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
        """
        Valida que el email sea único en el sistema.
        
        Returns:
            str: Email validado y limpio.
        
        Raises:
            ValidationError: Si el email no cumple con los requisitos.
        """
        email = self.cleaned_data.get("email").strip()
        if email is None:
            raise forms.ValidationError("El correo electrónico es obligatorio.")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ese email ya está registrado.")
        return email
    
    def clean_username(self):
        """
        Valida el nombre de usuario: unicidad, longitud y formato.
        
        Validaciones:
            - Longitud entre 4 y 20 caracteres
            - Solo caracteres alfanuméricos y guión bajo
            - Único en el sistema
        
        Returns:
            str: Username validado y limpio.
        
        Raises:
            ValidationError: Si el nombre de usuario no cumple con los requisitos.
        """
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
    """
    Formulario personalizado de inicio de sesión.
    
    Permite login con nombre de usuario o correo electrónico. Si se
    proporciona un email en el campo username, busca el usuario asociado
    y realiza la autenticación correspondiente.
    
    Tipo: AuthenticationForm (extiende)
    
    Campos:
        - username: Nombre de usuario o correo electrónico
        - password: Contraseña del usuario
    """
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': INPUT_CLASS, 'autofocus': True})
        self.fields['password'].widget.attrs.update({'class': INPUT_CLASS})
    
    def clean_username(self):
        """
        Permite login con username o email. Si es email, obtiene el username asociado.
        
        Returns:
            str: Username correspondiente al usuario.
        
        Raises:
            ValidationError: Si no existe cuenta con ese username/email.
        """
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
        """
        Valida que la contraseña no esté vacía.
        
        Returns:
            str: Contraseña validada.
        
        Raises:
            ValidationError: Si la contraseña está vacía.
        """
        password = self.cleaned_data.get("password").strip()
        if password is None:
            raise forms.ValidationError("La contraseña es obligatoria.")
        return password

class CustomSetPasswordForm(SetPasswordForm):
    """
    Formulario personalizado para establecer nueva contraseña.
    
    Usado en el flujo de recuperación de contraseña. Aplica estilos
    personalizados a los campos de contraseña.
    
    Tipo: SetPasswordForm (extiende)
    
    Campos:
        - new_password1: Nueva contraseña
        - new_password2: Confirmación de nueva contraseña
    """
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        f = self.fields
        f['new_password1'].widget.attrs.update({'class': INPUT_CLASS, 'placeholder': 'Ingresa tu nueva contraseña'})
        f['new_password2'].widget.attrs.update({'class': INPUT_CLASS, 'placeholder': 'Confirma tu nueva contraseña'})

class CustomPasswordResetForm(PasswordResetForm):
    """
    Formulario personalizado para solicitar recuperación de contraseña.
    
    Solicita el email del usuario para enviar instrucciones de
    recuperación de contraseña.
    
    Tipo: PasswordResetForm (extiende)
    
    Campos:
        - email: Correo electrónico registrado
    """
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.fields['email'].label = "Correo electrónico"
        self.fields['email'].widget.attrs.update({'class': INPUT_CLASS, 'placeholder': 'tucorreo@dominio.com', 'autocomplete': 'email'})


## FORMULARIO DE EDICIÓN DE USUARIO
class UserForm(forms.ModelForm):
    """
    Formulario para editar datos básicos del usuario autenticado.
    
    Permite modificar información personal del modelo User incluyendo
    validaciones de unicidad para username y email.
    
    Tipo: ModelForm
    Modelo: accounts.models.User
    
    Campos:
        - username: Nombre de usuario único
        - first_name: Nombre del usuario
        - last_name: Apellido del usuario
        - email: Correo electrónico único
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
        """
        Valida que el username no esté en uso por otro usuario.
        
        Returns:
            str: Username validado.
        
        Raises:
            ValidationError: Si el username ya existe (excluye el usuario actual).
        """
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ese nombre de usuario ya está en uso.")
        return username
    
    def clean_email(self):
        """
        Valida que el email no esté en uso por otro usuario.
        
        Returns:
            str: Email validado en minúsculas.
        
        Raises:
            ValidationError: Si el email ya existe (excluye el usuario actual).
        """
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ese email ya está registrado por otro usuario.")
        return email


# ============================================
# FORMULARIOS DE EDICIÓN DE PERFIL
# ============================================

class ProfileForm(forms.ModelForm):
    """
    Formulario completo para editar el perfil del usuario.
    
    Incluye todos los campos editables del modelo Perfil: información
    de contacto, descripción, URLs de imágenes, carrera y ramos cursados.
    
    Tipo: ModelForm
    Modelo: accounts.models.Perfil
    
    Campos:
        - telefono: Número de teléfono de contacto
        - descripcion: Biografía o presentación del usuario
        - foto_url: URL de foto de perfil externa
        - banner_url: URL de banner externo
        - carrera: Carrera universitaria
        - ramos_cursados: Ramos que ha cursado (selección múltiple)
    """
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
    """
    Formulario especializado para editar solo la descripción del perfil.
    
    Permite actualizar únicamente el campo de biografía/presentación
    sin afectar otros campos del perfil.
    
    Tipo: ModelForm
    Modelo: accounts.models.Perfil
    
    Campos:
        - descripcion: Texto biográfico del usuario
    """
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
    """
    Formulario especializado para editar imágenes del perfil.
    
    Permite cargar archivos de imagen localmente o proporcionar URLs
    externas tanto para foto de perfil como para banner.
    
    Tipo: ModelForm
    Modelo: accounts.models.Perfil
    
    Campos:
        - foto_url: URL externa de foto de perfil
        - banner_url: URL externa de banner
        - foto_file: Archivo de imagen para perfil
        - banner_file: Archivo de imagen para banner
    """
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
    """
    Formulario especializado para gestionar carrera y ramos cursados.
    
    Filtra dinámicamente los ramos disponibles para excluir los que ya
    fueron cursados, permitiendo agregar solo ramos nuevos sin duplicar.
    
    Tipo: ModelForm
    Modelo: accounts.models.Perfil
    
    Campos:
        - carrera: Carrera universitaria actual
        - ramos_cursados: Ramos nuevos a agregar (excluye ya cursados)
    """
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
        """
        Inicializa el formulario y filtra ramos para mostrar solo los no cursados.
        """
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
        """
        Guarda la carrera y agrega los nuevos ramos sin eliminar los existentes.
        
        Args:
            commit (bool): Si True, guarda inmediatamente en la base de datos.
        
        Returns:
            Perfil: Instancia del perfil actualizada.
        """
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
    """
    Formulario especializado para editar solo los ramos cursados.
    
    Permite gestionar la lista completa de ramos cursados con
    selección múltiple.
    
    Tipo: ModelForm
    Modelo: accounts.models.Perfil
    
    Campos:
        - ramos_cursados: Ramos que el usuario ha cursado
    """
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
    """
    Formulario especializado para editar solo la información de contacto.
    
    Permite actualizar únicamente el número de teléfono del perfil.
    
    Tipo: ModelForm
    Modelo: accounts.models.Perfil
    
    Campos:
        - telefono: Número de teléfono de contacto
    """
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