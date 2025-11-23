from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from .models import HorarioOfertado, OfertaClase, SolicitudClase, Comentario
from django.core.exceptions import ValidationError

INPUT = "appearance-none w-full px-4 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary transition"

class OfertaForm(forms.ModelForm):
    """
    Formulario para crear o editar una oferta de clase particular.
    
    Permite al usuario ingresar título, descripción y seleccionar un ramo
    de entre los que ha cursado. El campo de ramos se filtra dinámicamente
    según el perfil del usuario autenticado.
    
    Tipo: ModelForm
    Modelo: courses.models.OfertaClase
    
    Campos:
        - titulo: Título descriptivo de la oferta
        - descripcion: Detalles de la oferta
        - ramo: Ramo a enseñar (filtrado por ramos cursados del usuario)
    """
    titulo = forms.CharField(
        label="Título de la oferta",
        widget=forms.TextInput(attrs={
            "placeholder": "Ej: Álgebra I con enfoque en ejercicios",
            "class": INPUT
        })
    )

    class Meta:
        model = OfertaClase
        fields = ['titulo','descripcion','ramo']
        labels = {
            "descripcion": "Descripción",
            "ramo": "Ramo",
        }

        widgets = {
            "descripcion": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Cuenta brevemente el enfoque, requisitos, horarios tentativos...",
                "class": INPUT
            }),
            "ramo": forms.Select(attrs={
                "class": INPUT,
            }),
        }

    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario y filtra los ramos disponibles según
        los ramos cursados por el usuario autenticado.
        
        Args:
            user: Usuario autenticado (extraído de kwargs).
        """
        # Extraer el usuario del kwargs
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar ramos solo a los que el usuario ha cursado
        if user and hasattr(user, 'perfil'):
            self.fields['ramo'].queryset = user.perfil.ramos_cursados.all().order_by('name')
        
        # Mensaje cuando no hay ramos disponibles
        if not self.fields['ramo'].queryset.exists():
            self.fields['ramo'].empty_label = "No tienes ramos cursados registrados"
            

class HorarioOfertadoForm(forms.ModelForm):
    """
    Formulario para crear o editar un horario ofertado individual.
    
    Valida que la hora de inicio sea menor a la hora de fin y que
    los cupos totales sean al menos 1.
    
    Tipo: ModelForm
    Modelo: courses.models.HorarioOfertado
    
    Campos:
        - dia: Día de la semana (enum DiaSemana)
        - hora_inicio: Hora de inicio del horario
        - hora_fin: Hora de finalización del horario
        - cupos_totales: Cantidad de cupos disponibles
    """
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
        """
        Valida que el rango horario sea coherente y los cupos sean válidos.
        
        Validaciones:
            - hora_inicio debe ser menor que hora_fin
            - cupos_totales debe ser al menos 1
        
        Returns:
            dict: Datos limpiados y validados.
        
        Raises:
            ValidationError: Si el rango de horas es inválido o cupos < 1.
        """
        cleaned = super().clean()
        inicio = cleaned.get("hora_inicio")
        fin = cleaned.get("hora_fin")
        cupos = cleaned.get("cupos_totales")

        # Si algún campo requerido viene vacío, deja que el validador base lo marque.
        if inicio and fin:
            if inicio >= fin:
                self.add_error("hora_inicio", "La hora de inicio debe ser menor a la hora de término.")
                self.add_error("hora_fin", "La hora de término debe ser mayor a la hora de inicio.")
                raise ValidationError("Rango de horas inválido.")

        if cupos is not None and cupos < 1:
            self.add_error("cupos_totales", "Debe ser al menos 1.")

        return cleaned

class BaseHorarioFormSet(BaseInlineFormSet):
    """
    Formset personalizado para validar múltiples horarios ofertados.
    
    Asegura que al menos un horario válido sea agregado cuando se crea
    o edita una oferta de clase.
    
    Tipo: BaseInlineFormSet personalizado
    Modelo relacionado: HorarioOfertado
    """
    def clean(self):
        """
        Valida que se haya agregado al menos un horario ofertado válido.
        
        Ignora formularios vacíos o marcados para eliminar y cuenta solo
        los horarios con datos completos.
        
        Raises:
            ValidationError: Si no hay al menos un horario válido.
        """
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
"""
Factory de formset inline para gestionar múltiples horarios de una oferta.

Configuración:
    - Modelo padre: OfertaClase
    - Modelo hijo: HorarioOfertado
    - Formulario base: HorarioOfertadoForm
    - Formset personalizado: BaseHorarioFormSet
    - extra=1: Muestra un formulario vacío adicional
    - can_delete=True: Permite eliminar horarios existentes
"""

class SolicitudClaseForm(forms.ModelForm):
    """
    Formulario para crear o editar una solicitud de clase particular.
    
    Permite al usuario estudiante solicitar ayuda en un ramo específico,
    ingresando título, descripción y seleccionando el ramo deseado.
    
    Tipo: ModelForm
    Modelo: courses.models.SolicitudClase
    
    Campos:
        - titulo: Título descriptivo de la solicitud
        - descripcion: Detalles de lo que necesita aprender
        - ramo: Ramo en el que necesita ayuda
    """
    titulo = forms.CharField(
        label="Título de la solicitud",
        widget=forms.TextInput(attrs={
            "placeholder": "Ej: Ayuda con Cálculo I",
            "class": INPUT
        })
    )

    class Meta:
        model = SolicitudClase
        fields = ['titulo','descripcion','ramo']
        labels = {
            "descripcion": "Descripción",
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
            }),
        }

class ComentarioForm(forms.ModelForm):
    """
    Formulario para agregar comentarios a una oferta de clase.
    
    Permite a los usuarios dejar comentarios relacionados con una oferta
    específica, facilitando la comunicación y retroalimentación.
    
    Tipo: ModelForm
    Modelo: courses.models.ComentarioOferta
    
    Campos:
        - contenido: Texto del comentario
    """
    class Meta:
        model = Comentario
        fields = ['contenido']
        widgets = {
            "contenido": forms.Textarea(attrs={
                "class": "w-full p-3 rounded-xl border border-border bg-background",
                "rows": 3,
                "placeholder": "Escribe un comentario..."
            })
        }

   