from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from .models import HorarioOfertado, OfertaClase, SolicitudClase
from django.core.exceptions import ValidationError

INPUT = "appearance-none w-full px-4 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary transition"

class OfertaForm(forms.ModelForm):
    titulo = forms.CharField(
        label="Título de la oferta",
        widget=forms.TextInput(attrs={
            "placeholder": "Ej: Álgebra I con enfoque en ejercicios",
            "class": INPUT
        })
    )

    class Meta:
        model = OfertaClase
        fields = ['titulo','descripcion','ramos']
        labels = {
            "descripcion": "Descripción",
            "ramos": "Ramos asociados",
        }

        widgets = {
            "descripcion": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Cuenta brevemente el enfoque, requisitos, horarios tentativos...",
                "class": INPUT
            }),
            "ramos": forms.Select(attrs={
                "class": INPUT,
                "data-autocomplete-select": "true",
            }),
        }

    def clean_ramos(self):
        ramos = self.cleaned_data["ramos"]
        if len(ramos) > 1:
            raise forms.ValidationError("Solo puedes ofertar un ramo")
        if len(ramos) == 0:
            raise forms.ValidationError("Debes elegir un ramo para ofertar")
        return ramos
            

class HorarioOfertadoForm(forms.ModelForm):
    hora_inicio = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time", "class": INPUT}, format="%H:%M"),
        input_formats=["%H:%M"]
    )
    hora_fin = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time", "class": INPUT}, format="%H:%M"),
        input_formats=["%H:%M"]
    )
    class Meta:
        model = HorarioOfertado
        fields = ["dia", "hora_inicio", "hora_fin", "cupos_totales"]
        widgets = {
            "dia": forms.Select(attrs={"class": INPUT}),
            "cupos_totales": forms.NumberInput(attrs={"class": INPUT}),
        }

    def clean(self):
        cleaned = super().clean()
        inicio = cleaned.get("hora_inicio")
        fin = cleaned.get("hora_fin")
        cupos = cleaned.get("cupos_totales")

        # Si algún campo requerido viene vacío, deja que el validador base lo marque.
        if inicio and fin:
            if inicio >= fin:
                # Puedes marcar ambos campos o solo el "fin"
                self.add_error("hora_inicio", "La hora de inicio debe ser menor a la hora de término.")
                self.add_error("hora_fin", "La hora de término debe ser mayor a la hora de inicio.")
                raise ValidationError("Rango de horas inválido.")

        if cupos is not None and cupos < 1:
            self.add_error("cupos_totales", "Debe ser al menos 1.")

        return cleaned

class BaseHorarioFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        vivos = []
        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            cd = form.cleaned_data
            if cd.get("DELETE"):
                continue
            if not (cd.get("dia") and cd.get("hora_inicio") and cd.get("hora_fin")):
                continue
            vivos.append(cd)

        if len(vivos) == 0:
            raise ValidationError("Debes agregar al menos un horario ofertado.")

HorarioFormSet = inlineformset_factory(
    OfertaClase,
    HorarioOfertado,
    form=HorarioOfertadoForm,
    formset=BaseHorarioFormSet,
    fields=["dia", "hora_inicio", "hora_fin", "cupos_totales"],
    extra=1,
    can_delete=True,
)

class SolicitudClaseForm(forms.ModelForm):
    titulo = forms.CharField(
        label="Título de la solicitud",
        widget=forms.TextInput(attrs={
            "placeholder": "Ej: Ayuda con Cálculo I",
            "class": INPUT
        })
    )

    class Meta:
        model = SolicitudClase
        fields = ['titulo','descripcion','solicitante','ramo']
        labels = {
            "descripcion": "Descripción",
            "solicitante": "Solicitante",
            "ramo": "Ramo asociado",
        }

        widgets = {
            "descripcion": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Cuenta brevemente qué necesitas, tu disponibilidad, etc.",
                "class": INPUT
            }),
            "solicitante": forms.Select(attrs={"class": INPUT}),
            "ramo": forms.Select(attrs={
                "class": INPUT,
                "data-autocomplete-select": "true",
            }),
            #"modalidad": forms.Select(attrs={"class": INPUT}),
        }