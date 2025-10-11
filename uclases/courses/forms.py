from django import forms
from django.forms import inlineformset_factory
from .models import HorarioOfertado, OfertaClase
from .models import SolicitudClase
INPUT = "w-full px-4 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary transition"


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
        fields = ['titulo','descripcion','profesor','ramos']
        labels = {
            "descripcion": "Descripción",
            "profesor": "Profesor",
            "ramos": "Ramos asociados",
        }

        widgets = {
            "descripcion": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Cuenta brevemente el enfoque, requisitos, horarios tentativos…",
                "class": INPUT
            }),
            "profesor": forms.Select(attrs={"class": INPUT}),
            # Opciones:
            # 1) multiselect
            #"ramos": forms.SelectMultiple(attrs={"class": INPUT + " h-40"}),
            # 2) o casillas (quedan más lindas):
            "ramos": forms.CheckboxSelectMultiple(),
        }
        #help_texts = {
            #"ramos": "Mantén presionada Ctrl/⌘ para seleccionar varios (si usas multiselect).",
        #}

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

HorarioFormSet = inlineformset_factory(
    OfertaClase,
    HorarioOfertado,
    form=HorarioOfertadoForm,
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
        fields = ['titulo','descripcion','solicitante','ramo','modalidad']
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
            "ramo": forms.Select(attrs={"class": INPUT}),
            "modalidad": forms.Select(attrs={"class": INPUT}),
        }