from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from accounts.models import Perfil
from courses.models import Ramo, OfertaClase, HorarioOfertado, PerfilRamo, Inscripcion

User = get_user_model()

class AccountsModelTests(TestCase):
    """Pruebas para el comportamiento de modelos y señales en la app `accounts`.

    - Verifica que la señal post_save crea `Perfil` al crear un `User`.
    - Confirma que modificar y guardar el User no rompe la relación con Perfil.
    - Comprueba la relación m2m `ramos_cursados` y la restricción de unicidad
      en el modelo intermedio `PerfilRamo`.
    """

    def setUp(self):
        """Creamos un usuario base y obtenemos su perfil (esperando la señal)."""
        self.user = User.objects.create_user(username="test", email="test@example.com", password="x")
        # La señal debe crear el Perfil automáticamente
        self.perfil = Perfil.objects.get(user=self.user)
        self.ramo = Ramo.objects.create(name="Cálculo I")

    def test_signal_crea_perfil(self):
        """Crear un usuario nuevo debe crear automáticamente su `Perfil`."""
        u = User.objects.create_user(username="otro", email="otro@example.com", password="x")
        self.assertTrue(Perfil.objects.filter(user=u).exists())

    def test_signal_actualiza_perfil_si_usuario_se_guarda(self):
        """Guardar de nuevo el usuario no debe eliminar o romper el `Perfil`."""
        self.user.first_name = "A"
        self.user.save()
        self.perfil.refresh_from_db()  # sigue existiendo
        self.assertEqual(self.perfil.user.first_name, "A")

    def test_m2m_ramos_cursados_add(self):
        """Se puede agregar un `Ramo` al campo m2m `ramos_cursados` del perfil."""
        self.perfil.ramos_cursados.add(self.ramo)
        self.assertIn(self.ramo, self.perfil.ramos_cursados.all())

    def test_perfil_ramo_unique_constraint(self):
        """La relación intermedia `PerfilRamo` debe imponer unicidad por par.

        Intentar crear la misma relación dos veces debe lanzar `IntegrityError`.
        """
        PerfilRamo.objects.create(perfil=self.perfil, ramo=self.ramo)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                PerfilRamo.objects.create(perfil=self.perfil, ramo=self.ramo)

class InscripcionTests(TestCase):
    """Pruebas sobre la creación de `Inscripcion` y restricciones de unicidad."""

    def setUp(self):
        """Crear profesor y estudiante con sus perfiles (se generan por señal)."""
        self.user_p = User.objects.create_user(username="p", email="profesor@example.com", password="x")
        self.user_s = User.objects.create_user(username="s", email="estudiante@example.com", password="x")
        self.perfil_p = Perfil.objects.get(user=self.user_p)  # profesor
        self.perfil_s = Perfil.objects.get(user=self.user_s)  # estudiante

        # Crear ramo y oferta (ahora `ramo` es FK en OfertaClase)
        self.ramo = Ramo.objects.create(name="Álgebra")
        self.oferta = OfertaClase.objects.create(
            titulo="Álgebra 101",
            descripcion="Bases",
            profesor=self.perfil_p,
            ramo=self.ramo  # Ahora ramo es ForeignKey (un solo ramo)
        )

        # Crear un horario ofertado simple
        self.horario = HorarioOfertado.objects.create(
            dia=1, hora_inicio="10:00", hora_fin="11:00", cupos_totales=5, oferta=self.oferta
        )

    def test_inscripcion_unique_constraint(self):
        """Una misma pareja (estudiante, horario) no puede inscribirse dos veces."""
        Inscripcion.objects.create(estudiante=self.perfil_s, horario_ofertado=self.horario)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Inscripcion.objects.create(estudiante=self.perfil_s, horario_ofertado=self.horario)