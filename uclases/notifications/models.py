from django.db import models
from accounts.models import Perfil
from .enums import TipoNotificacion
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Notificacion(models.Model):
    destinatario = models.ForeignKey(Perfil, on_delete=models.CASCADE,related_name='notificaciones')
    tipo = models.CharField(max_length=50,choices=TipoNotificacion.choices)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    # Acción realizada (opcional)
    accion_realizada = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Acción que se realizó sobre esta notificación (ej: 'Aceptada', 'Rechazada')"
    )
    # Fecha de la acción realizada (opcional)
    fecha_accion = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha en que se realizó la acción"
    )

    # Relación genérica (puede apuntar a cualquier modelo)
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    objeto_relacionado = GenericForeignKey('content_type', 'object_id')
    
    # Timestamps
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
    
    def __str__(self):
        return f"{self.get_tipo_display()} para {self.destinatario.user.username}"
    
    
