from uuid import uuid4
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.forms import ValidationError
from django.utils import timezone
from django.urls import reverse

from courses.forms import HorarioOfertadoForm, HorarioFormSet, OfertaForm
from courses.models import OfertaClase, HorarioOfertado, Ramo, Perfil  # ajusta si la ruta cambia
from courses.enums import DiaSemana

User = get_user_model()

class FormFactoriesMixin:
    def make_user(self, username=None):
        if username is None:
            username = f"u_{uuid4().hex[:8]}"  # username siempre único
        return User.objects.create_user(username=username, password="x")

    def make_perfil(self, username=None):
        """
        - Crea el User con username único.
        - Si tu app tiene un signal post_save que ya crea Perfil, lo reutiliza.
        - Si no existe, lo crea explícitamente.
        """
        u = self.make_user(username)
        # Si tu signal ya creó el perfil, vendrá en u.perfil; si no, lo creamos.
        perfil = getattr(u, "perfil", None)
        if perfil is None:
            perfil, _ = Perfil.objects.get_or_create(user=u)
        return perfil

    def make_ramo(self, name="Álgebra I"):
        return Ramo.objects.create(name=name)

    def make_oferta(self, titulo="Oferta X"):
        perfil = self.make_perfil()  # crea user+perfil únicos
        oferta = OfertaClase.objects.create(
            titulo=titulo,
            descripcion="desc",
            profesor=perfil,
        )
        # si tu modelo exige ramos, agrega al menos uno:
        ramo = self.make_ramo()
        oferta.ramos.add(ramo)
        return oferta

    def build_formset_post(self, prefix, forms):
        """
        Construye un payload POST válido para el inline formset.
        forms: lista de dicts con los campos por fila.
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
    def test_invalid_when_end_before_or_equal_start(self):
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

        form_equal = HorarioOfertadoForm(data={
            "dia": DiaSemana.LUNES,
            "hora_inicio": "10:00",
            "hora_fin": "10:00",
            "cupos_totales": 1,
        })
        self.assertFalse(form_equal.is_valid())
        self.assertIn("Rango de horas inválido.", form_equal.non_field_errors())

    def test_invalid_when_cupos_less_than_one(self):
        form = HorarioOfertadoForm(data={
            "dia": DiaSemana.MARTES,
            "hora_inicio": "10:00",
            "hora_fin": "11:00",
            "cupos_totales": 0,
        })
        self.assertFalse(form.is_valid())
        self.assertIn("cupos_totales", form.errors)

    def test_valid_form(self):
        form = HorarioOfertadoForm(data={
            "dia": DiaSemana.MIERCOLES,
            "hora_inicio": "08:30",
            "hora_fin": "10:00",
            "cupos_totales": 5,
        })
        self.assertTrue(form.is_valid())


class BaseHorarioFormSetTests(FormFactoriesMixin, TestCase):
    def test_requires_at_least_one_horario(self):
        oferta = self.make_oferta()
        prefix = "horarios"
        post = self.build_formset_post(prefix, forms=[{}])  # fila vacía
        formset = HorarioFormSet(post, instance=oferta, prefix=prefix)
        self.assertFalse(formset.is_valid())
        self.assertIn("Debes agregar al menos un horario ofertado.", formset.non_form_errors())

    def test_valid_with_one_complete_row(self):
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
        self.assertEqual(HorarioOfertado.objects.filter(oferta=oferta).count(), 1)

class OfertaFormRamosTests(FormFactoriesMixin, TestCase):
    """
    SOLO si agregas en OfertaForm.clean() la validación de 'al menos un ramo'.
    Si no la agregas, puedes borrar esta clase.
    """
    def test_requires_at_least_one_ramo(self):
        perfil = self.make_perfil("profe_ramos")
        form = OfertaForm(data={
            "titulo": "X",
            "descripcion": "Y",
            "profesor": perfil.pk,
            # "ramos": []  # sin ramos
        })
        self.assertFalse(form.is_valid())
        self.assertIn("ramos", form.errors)

    def test_valid_with_one_ramo(self):
        perfil = self.make_perfil("profe_ok")
        ramo = self.make_ramo("Cálculo")
        form = OfertaForm(data={
            "titulo": "X",
            "descripcion": "Y",
            "profesor": perfil.pk,
            "ramos": [ramo.pk],
        })
        self.assertTrue(form.is_valid())