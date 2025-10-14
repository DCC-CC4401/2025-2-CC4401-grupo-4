from uuid import uuid4
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.forms import ValidationError
from django.utils import timezone
from django.urls import reverse

from courses.forms import HorarioOfertadoForm, HorarioFormSet, OfertaForm, SolicitudClaseForm
from courses.models import OfertaClase, HorarioOfertado, Ramo, Perfil  # ajusta si la ruta cambia
from courses.enums import DiaSemana

User = get_user_model()

class FormFactoriesMixin:
    """
    Mixin helper para construir objetos frequently-used en los tests.

    Proporciona fábricas pequeñas (users, perfiles, ramos, ofertas) para
    mantener los tests legibles y evitar repetición.
    """

    def make_user(self, username=None):
        """Crear y devolver un User con username único.

        Si no se pasa username, se genera uno corto y único usando uuid4.
        La contraseña por defecto es "x" para simplificar autenticación en
        tests que lo requieran.
        """
        if username is None:
            username = f"u_{uuid4().hex[:8]}"  # username siempre único
        return User.objects.create_user(username=username, password="x")

    def make_perfil(self, username=None):
        """Crear un User y devolver su Perfil.

        Si la aplicación define una señal que crea `Perfil` tras crear el
        `User`, este método la aprovechará. Si por alguna razón no existe
        el perfil, se crea con `get_or_create`.
        """
        u = self.make_user(username)
        # Si tu signal ya creó el perfil, vendrá en u.perfil; si no, lo creamos.
        perfil = getattr(u, "perfil", None)
        if perfil is None:
            perfil, _ = Perfil.objects.get_or_create(user=u)
        return perfil

    def make_ramo(self, name="Álgebra I"):
        """Crear y devolver un `Ramo` con el nombre dado."""
        return Ramo.objects.create(name=name)

    def make_oferta(self, titulo="Oferta X"):
        """Crear y devolver una `OfertaClase` simple asociada a un perfil y ramo."""
        perfil = self.make_perfil()
        ramo = self.make_ramo()
        oferta = OfertaClase.objects.create(
            titulo=titulo,
            descripcion="desc",
            profesor=perfil,
            ramo=ramo,
        )
        return oferta

    def build_formset_post(self, prefix, forms):
        """Construir el payload POST que espera un inline formset.

        `prefix` es el prefijo del formset (ej. "horarios").
        `forms` es una lista de diccionarios con los campos por fila.
        Devuelve un dict que puede pasarse como datos POST al formset.
        """
        data = {
            f"{prefix}-TOTAL_FORMS": str(len(forms)),
            f"{prefix}-INITIAL_FORMS": "0",
            f"{prefix}-MIN_NUM_FORMS": "0",
            f"{prefix}-MAX_NUM_FORMS": "1000",
        }
        for i, row in enumerate(forms):
            for k, v in row.items():
                data[f"{prefix}-{i}-{k}"] = v
        return data


class HorarioOfertadoFormTests(TestCase):
    """Tests unitarios para la validación de `HorarioOfertadoForm`.

    Verifica reglas como:
    - `hora_fin` debe ser posterior a `hora_inicio`.
    - `cupos_totales` debe ser al menos 1.
    """

    def test_invalid_when_end_before_or_equal_start(self):
        """Hora fin anterior o igual a inicio -> formulario inválido.

        Comprueba que se agrega un error no-field (mensaje global) y que
        los campos `hora_inicio` y `hora_fin` aparecen en los errores.
        """
        form = HorarioOfertadoForm(data={
            "dia": DiaSemana.LUNES,
            "hora_inicio": "10:00",
            "hora_fin": "09:59",
            "cupos_totales": 1,
        })
        self.assertFalse(form.is_valid())
        self.assertIn("Rango de horas inválido.", form.non_field_errors())
        self.assertIn("hora_inicio", form.errors)
        self.assertIn("hora_fin", form.errors)

        # También probamos el caso de horas iguales
        form_equal = HorarioOfertadoForm(data={
            "dia": DiaSemana.LUNES,
            "hora_inicio": "10:00",
            "hora_fin": "10:00",
            "cupos_totales": 1,
        })
        self.assertFalse(form_equal.is_valid())
        self.assertIn("Rango de horas inválido.", form_equal.non_field_errors())

    def test_invalid_when_cupos_less_than_one(self):
        """`cupos_totales` menor que 1 -> error en campo `cupos_totales`."""
        form = HorarioOfertadoForm(data={
            "dia": DiaSemana.MARTES,
            "hora_inicio": "10:00",
            "hora_fin": "11:00",
            "cupos_totales": 0,
        })
        self.assertFalse(form.is_valid())
        self.assertIn("cupos_totales", form.errors)

    def test_valid_form(self):
        """Caso válido simple: formulario pasa la validación."""
        form = HorarioOfertadoForm(data={
            "dia": DiaSemana.MIERCOLES,
            "hora_inicio": "08:30",
            "hora_fin": "10:00",
            "cupos_totales": 5,
        })
        self.assertTrue(form.is_valid())


class BaseHorarioFormSetTests(FormFactoriesMixin, TestCase):
    """Tests para el `HorarioFormSet` usado como inline formset en `OfertaClase`.

    Valida reglas del formset como requerir al menos un horario y guardar
    correctamente las filas válidas.
    """

    def test_requires_at_least_one_horario(self):
        """Formset con una fila vacía debe ser inválido y mostrar error no-form."""
        oferta = self.make_oferta()
        prefix = "horarios"
        post = self.build_formset_post(prefix, forms=[{}])  # fila vacía
        formset = HorarioFormSet(post, instance=oferta, prefix=prefix)
        self.assertFalse(formset.is_valid())
        self.assertIn("Debes agregar al menos un horario ofertado.", formset.non_form_errors())

    def test_valid_with_one_complete_row(self):
        """Formset con una fila completa debería validarse y crear el registro."""
        oferta = self.make_oferta()
        prefix = "horarios"
        post = self.build_formset_post(prefix, forms=[{
            "dia": DiaSemana.JUEVES,
            "hora_inicio": "09:00",
            "hora_fin": "10:00",
            "cupos_totales": 3,
        }])
        formset = HorarioFormSet(post, instance=oferta, prefix=prefix)
        self.assertTrue(formset.is_valid())
        formset.save()
        # Se espera exactamente 1 horario asociado a la oferta creada
        self.assertEqual(HorarioOfertado.objects.filter(oferta=oferta).count(), 1)

class OfertaFormRamosTests(FormFactoriesMixin, TestCase):
    """Pruebas para la validación del `OfertaForm` relacionado a `ramo`.

    El formulario debe requerir un ramo (ForeignKey). Aquí probamos casos
    donde falta el ramo y donde se provee uno válido.
    """

    def test_requires_at_least_one_ramo(self):
        """Sin ramo -> formulario inválido y campo `ramo` en errores."""
        form = OfertaForm(data={
            "titulo": "X",
            "descripcion": "Y",
            # "ramo": None  # sin ramo
        })
        self.assertFalse(form.is_valid())
        self.assertIn("ramo", form.errors)

    def test_valid_with_one_ramo(self):
        """Con un ramo existente el formulario debe ser válido."""
        ramo = self.make_ramo("Cálculo")
        form = OfertaForm(data={
            "titulo": "X",
            "descripcion": "Y",
            "ramo": ramo.pk,
        })
        self.assertTrue(form.is_valid())

    def test_invalid_with_multiple_ramos(self):
        """Historicamente había tests para múltiples ramos, pero el modelo
        ahora acepta un solo `ramo` (ForeignKey). Este test comprueba que
        la validación con un ramo individual sigue siendo válida.
        """
        ramo1 = self.make_ramo("Cálculo")
        form = OfertaForm(data={
            "titulo": "X",
            "descripcion": "Y",
            "ramo": ramo1.pk,
        })
        # Ahora debería ser válido porque solo acepta un ramo
        self.assertTrue(form.is_valid())


class SolicitudClaseFormTests(FormFactoriesMixin, TestCase):
    """Tests para `SolicitudClaseForm` que valida presencia de `ramo` y `titulo`."""

    def test_requires_ramo(self):
        """Sin ramo -> formulario inválido y error en campo `ramo`."""
        form = SolicitudClaseForm(data={
            "titulo": "Solicitud X",
            "descripcion": "Necesito ayuda",
            # Falta ramo
        })
        self.assertFalse(form.is_valid())
        self.assertIn("ramo", form.errors)

    def test_valid_with_ramo(self):
        """Con ramo -> formulario válido."""
        ramo = self.make_ramo("Física")
        form = SolicitudClaseForm(data={
            "titulo": "Solicitud X",
            "descripcion": "Necesito ayuda",
            "ramo": ramo.pk,
        })
        self.assertTrue(form.is_valid())

    def test_titulo_required(self):
        """Si falta título el formulario debe ser inválido y reportar `titulo`."""
        ramo = self.make_ramo("Química")
        form = SolicitudClaseForm(data={
            # Falta título
            "descripcion": "desc",
            "ramo": ramo.pk,
        })
        self.assertFalse(form.is_valid())
        self.assertIn("titulo", form.errors)