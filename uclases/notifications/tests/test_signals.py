from courses.models import Inscripcion
from courses.enums import EstadoInscripcion
from notifications.models import Notification
from notifications.enums import NotificationTypes
from django.utils import timezone
from .test_base import NotificationBaseTests

class InscriptionSignalTest(NotificationBaseTests):
    def test_inscription_created_notification(self):
        inscription = Inscripcion.objects.create(
            estudiante=self.perfil_estudiante,
            horario_ofertado=self.horario,
            estado=EstadoInscripcion.PENDIENTE,
            fecha_reserva=timezone.now()
        )
        
        self.assertEqual(Notification.objects.count(), 1)
        n = Notification.objects.first()

        self.assertEqual(n.receiver, self.perfil_profe)
        self.assertEqual(n.type, NotificationTypes.INSCRIPTION_CREATED)


    def test_inscription_accepted_notification(self):
        inscription = Inscripcion.objects.create(
            estudiante=self.perfil_estudiante,
            horario_ofertado=self.horario,
            estado=EstadoInscripcion.PENDIENTE,
            fecha_reserva=timezone.now()
        )
        Notification.objects.all().delete() 
        inscription.estado = EstadoInscripcion.ACEPTADO
        inscription.save()

        self.assertEqual(Notification.objects.count(), 1)
        n = Notification.objects.first()
        self.assertEqual(n.receiver, self.perfil_estudiante)
        self.assertEqual(n.type, NotificationTypes.INSCRIPTION_ACCEPTED)