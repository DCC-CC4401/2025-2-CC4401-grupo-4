from courses.models import Inscripcion
from courses.enums import EstadoInscripcion
from notifications.models import Notification
from notifications.enums import NotificationTypes
from django.utils import timezone
from .test_base import NotificationBaseTests

class InscriptionSignalTest(NotificationBaseTests):

    def test_inscription_created_notifies_professor(self):
        """Caso 1: Al crear inscripción PENDIENTE -> Notifica al Profesor."""
        Inscripcion.objects.create(
            estudiante=self.perfil_estudiante,
            horario_ofertado=self.horario,
            estado=EstadoInscripcion.PENDIENTE,
            fecha_reserva=timezone.now()
        )
        
        self.assertEqual(Notification.objects.count(), 1)
        notif = Notification.objects.first()
        self.assertEqual(notif.receiver, self.perfil_profe) # Valida receptor
        self.assertEqual(notif.type, NotificationTypes.INSCRIPTION_CREATED)

    def test_inscription_accepted_notifies_student(self):
        """Caso 2: Al ACEPTAR -> Notifica al Estudiante."""
        ins = self._create_dummy_inscription()
        
        ins.estado = EstadoInscripcion.ACEPTADO
        ins.save()

        self.assertEqual(Notification.objects.count(), 1)
        notif = Notification.objects.first()
        self.assertEqual(notif.receiver, self.perfil_estudiante) # Valida receptor
        self.assertEqual(notif.type, NotificationTypes.INSCRIPTION_ACCEPTED)

    def test_inscription_rejected_notifies_student(self):
        """Caso 3: Al RECHAZAR -> Notifica al Estudiante."""
        ins = self._create_dummy_inscription()
        
        ins.estado = EstadoInscripcion.RECHAZADO
        ins.save()

        self.assertEqual(Notification.objects.count(), 1)
        notif = Notification.objects.first()
        self.assertEqual(notif.receiver, self.perfil_estudiante)
        self.assertEqual(notif.type, NotificationTypes.INSCRIPTION_REJECTED)

    def test_inscription_canceled_notifies_professor(self):
        """Caso 4: Al CANCELAR -> Notifica al Profesor (el alumno cancela)."""
        ins = self._create_dummy_inscription()
        
        ins.estado = EstadoInscripcion.CANCELADO
        ins.save()

        self.assertEqual(Notification.objects.count(), 1)
        notif = Notification.objects.first()
        self.assertEqual(notif.receiver, self.perfil_profe) # Ojo: aquí recibe el profe
        self.assertEqual(notif.type, NotificationTypes.INSCRIPTION_CANCELED)

    def test_no_notification_if_state_unchanged(self):
        """Caso 5: Si guardo sin cambiar estado, NO debe duplicar notificaciones."""
        ins = self._create_dummy_inscription()
        
        # Guardo de nuevo el mismo estado
        ins.estado = EstadoInscripcion.PENDIENTE
        ins.save()

        # Count debe seguir siendo 0 (porque borramos la inicial en el helper)
        self.assertEqual(Notification.objects.count(), 0)

    # --- Helper para no repetir código ---
    def _create_dummy_inscription(self):
        ins = Inscripcion.objects.create(
            estudiante=self.perfil_estudiante,
            horario_ofertado=self.horario,
            estado=EstadoInscripcion.PENDIENTE,
            fecha_reserva=timezone.now()
        )
        Notification.objects.all().delete() # Limpieza inicial
        return ins