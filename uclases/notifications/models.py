from django.db import models
from accounts.models import Perfil
from .enums import NotificationTypes
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from notifications.strategy.factory import NotificationStrategyFactory

class Notification(models.Model):
    receiver = models.ForeignKey(Perfil, on_delete=models.CASCADE,related_name='notifications')
    type = models.CharField(max_length=50,choices=NotificationTypes.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    read = models.BooleanField(default=False)
    # Acción realizada (opcional)
    action_taken = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Acción que se realizó sobre esta notificación (ej: 'Aceptada', 'Rechazada')"
    )
    # Fecha de la acción realizada (opcional)
    action_date = models.DateTimeField(
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
    related_object = GenericForeignKey('content_type', 'object_id')
    
    # Timestamps
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-creation_date']  # Más recientes primero
    
    def __str__(self):
        return f"{self.title} - {self.receiver.user.username}"
    
    def get_icon(self):
        """
        Retorna el ícono asociado a este tipo de notificación.
        Utiliza el patrón Strategy.
        """
        strategy = NotificationStrategyFactory.get_strategy(self.type)
        return strategy.get_icon()
    
    def get_available_actions(self):
        """
        Retorna las acciones disponibles para esta notificación.
        Utiliza el patrón Strategy.
        """
        strategy = NotificationStrategyFactory.get_strategy(self.type)
        return strategy.get_actions(self)
    
