from django import forms
from django.forms import inlineformset_factory
from .models import HorarioOfertado, OfertaClase

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
        help_texts = {
            #"ramos": "Mantén presionada Ctrl/⌘ para seleccionar varios (si usas multiselect).",
        }

HorarioFormSet = inlineformset_factory(
    parent_model=OfertaClase,
    model=HorarioOfertado,
    fields=["dia", "hora_inicio", "hora_fin", "cupos_totales"],
    extra=1,             # cuántos formularios vacíos mostrar por defecto
    can_delete=True,     # permite eliminar horarios
)