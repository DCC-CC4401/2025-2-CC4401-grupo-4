from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Perfil

#Automatización de la creación de PERFIL:
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_o_actualizar_perfil(sender, instance, created, **kwargs): 
    if created:
        Perfil.objects.create(user=instance)
    else: 
        Perfil.objects.get_or_create(user=instance)
