from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid 
from django.core.validators import RegexValidator
solo_alnum_guionbajo = RegexValidator(
    r'^[a-zA-Z0-9_]+$',
    'Usa solo letras, números o guión bajo (_), sin espacios ni acentos.'
)

class User(AbstractUser):
    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        help_text='Solo letras, números o _',
        validators=[solo_alnum_guionbajo],   
        error_messages={'unique': 'Ese nombre de usuario ya existe.'},
    )
    public_uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    email = models.EmailField(verbose_name=("correo electrónico"), unique=True)