from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import uuid 
from django.core.validators import RegexValidator
solo_alnum_guionbajo = RegexValidator(
    r'^[a-zA-Z0-9_]+$',
    'Usa solo letras, números o guión bajo (_), sin espacios ni acentos.'
)

class User(AbstractUser):
    """
    Usuario personalizado que extiende AbstractUser de Django.
    
    Representa un usuario del sistema con autenticación y un identificador
    público único (UUID) para compartir perfiles sin exponer el ID interno.
    
    Attributes:
        username (CharField): Nombre de usuario único, solo alfanumérico y guión bajo.
        public_uid (UUIDField): Identificador público único para URLs compartibles.
        email (EmailField): Correo electrónico único del usuario.
    
    Relationships:
        - OneToOne con Perfil (a través de Perfil.user)
    """
    username = models.CharField(
        'Nombre de usuario',
        max_length=150,
        unique=True,
        help_text='Solo letras, números o _',
        validators=[solo_alnum_guionbajo],   
        error_messages={'unique': 'Ese nombre de usuario ya existe.'},
    )
    public_uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    email = models.EmailField(verbose_name=("correo electrónico"), unique=True)

# Perfil:
class Perfil(models.Model):
    """
    Perfil extendido de usuario con información académica y de contacto.
    
    Almacena información adicional del usuario incluyendo foto de perfil,
    banner, descripción, carrera, ramos cursados y estadísticas de ratings.
    
    Attributes:
        user (OneToOneField): Usuario de Django asociado (PK).
        telefono (CharField): Número de teléfono de contacto opcional.
        descripcion (TextField): Descripción del usuario.
        foto_url (URLField): URL externa de foto de perfil.
        foto_file (ImageField): Archivo de imagen de perfil subido localmente.
        banner_file (ImageField): Imagen de banner para el perfil subida localmente.
        banner_url (URLField): URL externa de banner.
        rating_promedio (DecimalField): Promedio de calificaciones recibidas (0-5).
        total_ratings (IntegerField): Cantidad total de calificaciones recibidas.
        carrera (ForeignKey): Carrera universitaria del usuario.
        ramos_cursados (ManyToManyField): Ramos que el usuario ha cursado.
    
    Relationships:
        - OneToOne con User (usuario asociado)
        - ForeignKey a courses.Carrera (carrera del usuario)
        - ManyToMany con courses.Ramo a través de courses.PerfilRamo
        - Reverse relations: ofertas_creadas, solicitudes_creadas, inscripciones,
          ratings_dados, ratings_recibidos, comentarios_publicados
    
    Meta:
        verbose_name_plural = "Perfiles"
    """
    # Relación 1:1 con User basico de Django,
    # user = ID_Usuario (PK)/(FK)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key = True)
    #Atributos de PERFIL:
    telefono = models.CharField(max_length=13, blank=True, null=True)
    descripcion = models.TextField(max_length=500, blank=True)
    foto_url = models.URLField(max_length=200, blank=True, null=True)
    foto_file = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    banner_file = models.ImageField(upload_to='banners/', blank=True, null=True)
    banner_url = models.URLField(max_length=200, blank=True, null=True)
    rating_promedio = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_ratings = models.IntegerField(default=0)
    # Relación N:1 con CARRERA (Una CARRERA es cursada por N Perfiles)
    # ID Carrera (FK)
    carrera = models.ForeignKey('courses.Carrera', on_delete=models.SET_NULL, null=True, blank=True, related_name='perfiles_cursando')
    ramos_cursados = models.ManyToManyField(
        'courses.Ramo',               
        through='courses.PerfilRamo',
        related_name='perfiles_que_cursaron',
        blank=True,
    )

    class Meta: verbose_name_plural = "Perfiles"
    def __str__(self): return f"Perfil de {self.user.username}"