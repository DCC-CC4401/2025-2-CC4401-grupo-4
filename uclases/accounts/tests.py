from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from accounts.models import Perfil
from courses.models import Ramo, OfertaClase, HorarioOfertado, PerfilRamo, Inscripcion

User = get_user_model()

class AccountsModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", email="test@example.com", password="x")
        # La señal debe crear el Perfil automáticamente
        self.perfil = Perfil.objects.get(user=self.user)
        self.ramo = Ramo.objects.create(name="Cálculo I")

    def test_signal_crea_perfil(self):
        u = User.objects.create_user(username="otro", email="otro@example.com", password="x")
        self.assertTrue(Perfil.objects.filter(user=u).exists())

    def test_signal_actualiza_perfil_si_usuario_se_guarda(self):
        # No debe romper si el usuario se guarda otra vez
        self.user.first_name = "A"
        self.user.save()
        self.perfil.refresh_from_db()  # sigue existiendo
        self.assertEqual(self.perfil.user.first_name, "A")

    def test_m2m_ramos_cursados_add(self):
        self.perfil.ramos_cursados.add(self.ramo)
        self.assertIn(self.ramo, self.perfil.ramos_cursados.all())

    def test_perfil_ramo_unique_constraint(self):
        PerfilRamo.objects.create(perfil=self.perfil, ramo=self.ramo)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                PerfilRamo.objects.create(perfil=self.perfil, ramo=self.ramo)

class InscripcionTests(TestCase):
    def setUp(self):
        self.user_p = User.objects.create_user(username="p", email="profesor@example.com", password="x")
        self.user_s = User.objects.create_user(username="s", email="estudiante@example.com", password="x")
        self.perfil_p = Perfil.objects.get(user=self.user_p)  # profesor
        self.perfil_s = Perfil.objects.get(user=self.user_s)  # estudiante

        self.ramo = Ramo.objects.create(name="Álgebra")
        self.oferta = OfertaClase.objects.create(
            titulo="Álgebra 101",
            descripcion="Bases",
            profesor=self.perfil_p,
        )
        self.oferta.ramos.add(self.ramo)

        self.horario = HorarioOfertado.objects.create(
            dia=1, hora_inicio="10:00", hora_fin="11:00", cupos_totales=5, oferta=self.oferta
        )

    def test_inscripcion_unique_constraint(self):
        Inscripcion.objects.create(estudiante=self.perfil_s, horario_ofertado=self.horario)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Inscripcion.objects.create(estudiante=self.perfil_s, horario_ofertado=self.horario)