from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from notifications.strategy.factory import NotificationStrategyFactory
from notifications.strategy.trait import NotificationStrategy
from notifications.enums import NotificationTypes
from courses.models import Ramo, OfertaClase, HorarioOfertado
import datetime
import uuid

User = get_user_model()

class TestStrategyBase(NotificationStrategy):
    def get_title(self, data):
        return "Título Test"
    def get_message(self, data):
        return "Mensaje Test"
    def get_actions(self, data):
        return []
    def get_icon(self): 
        return "test-icon"

class NotificationBaseTests(TestCase):
    def setUp(self):
        self.strategy_types = [
            NotificationTypes.INSCRIPTION_CREATED,
            NotificationTypes.INSCRIPTION_ACCEPTED,
            NotificationTypes.INSCRIPTION_REJECTED,
            NotificationTypes.INSCRIPTION_CANCELED,
            "NOTIFICATION_TEST_TYPE"
        ]

        for type in self.strategy_types:
            NotificationStrategyFactory.register(type)(TestStrategyBase)
        self.professor = User.objects.create_user(
            username = 'profesor_base',
            password = 'password123',
            email = 'profesor@test.cl',
            public_uid = uuid.uuid4().hex
        )
        self.perfil_profe = self.professor.perfil

        self.estudiante = User.objects.create_user(
            username = 'estudiante_base',
            password = 'password123',
            email = 'estudiante@test.cl',
            public_uid = uuid.uuid4().hex
        )
        self.perfil_estudiante = self.estudiante.perfil

        self.ramo = Ramo.objects.create(name = "Ramo de Prueba")

        self.oferta = OfertaClase.objects.create(
            titulo = "Oferta de Prueba",
            descripcion = "Descripción de la oferta de prueba",
            profesor = self.perfil_profe,
            ramo = self.ramo,
            public = True,
            fecha_publicacion = timezone.now()

        )



        self.horario = HorarioOfertado.objects.create(
            oferta = self.oferta,
            dia = 1,
            hora_inicio = datetime.time(10, 0),
            hora_fin = datetime.time(12, 0),
            cupos_totales = 12
        )