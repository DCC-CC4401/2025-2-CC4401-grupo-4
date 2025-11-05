"""
Servicio para manejar la lógica de negocio de inscripciones.

Este servicio encapsula toda la lógica relacionada con aceptar, rechazar
y cancelar inscripciones, incluyendo la actualización de notificaciones
asociadas.
"""

from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from courses.enums import EstadoInscripcion


class InscriptionService:
    """
    Servicio que maneja las operaciones sobre inscripciones.
    
    Responsabilidades:
    - Validar permisos y estados
    - Ejecutar cambios de estado en inscripciones
    - Actualizar notificaciones relacionadas
    - Manejar lógica de cupos
    """
    
    @staticmethod
    def accept_inscription(inscription, user):
        """
        Acepta una inscripción pendiente.
        
        Valida permisos, cambia el estado de la inscripción,
        reduce cupos y actualiza la notificación si existe.
        
        Args:
            inscription: Instancia de Inscripcion a aceptar
            user: Usuario que realiza la acción (debe ser el profesor)
        
        Returns:
            tuple: (success: bool, message: str)
        """
        offer = inscription.horario_ofertado.oferta
        
        # Validar permisos
        if offer.profesor != user.perfil:
            return False, "No tienes permiso para gestionar esta inscripción."
        
        # Validar estado
        if inscription.estado != EstadoInscripcion.PENDIENTE:
            return False, "Esta inscripción ya fue procesada."
        
        # Ejecutar acción
        inscription.aceptar()
        
        # Reducir cupos
        schedule = inscription.horario_ofertado
        schedule.cupos_totales -= 1
        schedule.save()
        
        # Actualizar notificación relacionada (si existe)
        InscriptionService._update_notification(
            inscription=inscription,
            action_text="Aceptada ✅"
        )
        
        student_name = inscription.estudiante.user.get_full_name()
        return True, f"Inscripción de {student_name} aceptada."
    
    @staticmethod
    def reject_inscription(inscription, user):
        """
        Rechaza una inscripción pendiente.
        
        Valida permisos, cambia el estado de la inscripción
        y actualiza la notificación si existe.
        
        Args:
            inscription: Instancia de Inscripcion a rechazar
            user: Usuario que realiza la acción (debe ser el profesor)
        
        Returns:
            tuple: (success: bool, message: str)
        """
        offer = inscription.horario_ofertado.oferta
        
        # Validar permisos
        if offer.profesor != user.perfil:
            return False, "No tienes permiso para gestionar esta inscripción."
        
        # Validar estado
        if inscription.estado != EstadoInscripcion.PENDIENTE:
            return False, "Esta inscripción ya fue procesada."
        
        # Ejecutar acción
        inscription.rechazar()
        
        # Actualizar notificación relacionada (si existe)
        InscriptionService._update_notification(
            inscription=inscription,
            action_text="Rechazada ❌"
        )
        
        student_name = inscription.estudiante.user.get_full_name()
        return True, f"Inscripción de {student_name} rechazada."
    
    @staticmethod
    def cancel_inscription(inscription, user):
        """
        Cancela una inscripción (solo puede hacerlo el estudiante).
        
        Valida permisos, cambia el estado de la inscripción,
        devuelve cupos si estaba aceptada y actualiza la notificación.
        
        Args:
            inscription: Instancia de Inscripcion a cancelar
            user: Usuario que realiza la acción (debe ser el estudiante)
        
        Returns:
            tuple: (success: bool, message: str)
        """
        # Validar permisos
        if inscription.estudiante != user.perfil:
            return False, "No puedes cancelar una inscripción que no es tuya."
        
        # Validar estado
        if inscription.estado not in [EstadoInscripcion.PENDIENTE, EstadoInscripcion.ACEPTADO]:
            return False, "Esta inscripción no puede ser cancelada."
        
        # Devolver cupo si estaba aceptada
        if inscription.estado == EstadoInscripcion.ACEPTADO:
            schedule = inscription.horario_ofertado
            schedule.cupos_totales += 1
            schedule.save()
        
        # Ejecutar acción
        inscription.cancelar()
        
        # Actualizar notificación relacionada (si existe)
        InscriptionService._update_notification(
            inscription=inscription,
            action_text="Cancelada 🚫"
        )
        
        return True, "Tu inscripción ha sido cancelada exitosamente."
    
    @staticmethod
    def _update_notification(inscription, action_text):
        """
        Actualiza la notificación relacionada con una inscripción.
        
        Busca la notificación asociada a la inscripción y la marca como
        leída, agregando el texto de la acción realizada.
        
        Args:
            inscription: Instancia de Inscripcion
            action_text: Texto descriptivo de la acción (ej: "Aceptada ✅")
        """
        try:
            # Importar aquí para evitar circular imports
            from notifications.models import Notification
            from notifications.enums import NotificationTypes
            
            # Buscar la notificación relacionada
            content_type = ContentType.objects.get_for_model(inscription)
            notification = Notification.objects.filter(
                content_type=content_type,
                object_id=inscription.id,
                type=NotificationTypes.INSCRIPTION_CREATED
            ).first()
            
            # Si existe, actualizarla
            if notification:
                notification.read = True
                notification.action_taken = action_text
                notification.action_date = timezone.now()
                notification.save()
                
        except ImportError:
            # Si el módulo notifications no existe, ignorar silenciosamente
            pass
        except Exception:
            # Si hay cualquier otro error, no fallar la operación principal
            pass
