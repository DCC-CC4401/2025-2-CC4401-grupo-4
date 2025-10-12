from django.db import models
from accounts.models import Perfil
from .enums import DiaSemana, EstadoInscripcion
from django.core.validators import MinValueValidator, MaxValueValidator


#Carrera:
class Carrera(models.Model):
    #ID_Carrera (PK) se crea automaticamente como 'id'
    name = models.CharField(max_length=100)

    class Meta: verbose_name_plural = "Carreras"

    def __str__(self): return self.name

#Ramo:
class Ramo(models.Model):
    #ID_Ramo (PK) se crea automaticamente como 'id'
    name = models.CharField(max_length=100)

    def __str__(self): return self.name

#Oferta Clase:
class OfertaClase(models.Model):
    #ID_Oferta (PK) se crea atomaticamente como 'id'
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

    #Relación N:1 con PERFIL (Profesor)
    #ID Usuario (Profesor) (FK)
    profesor = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name= 'ofertas_creadas')

    #Relación N:M con RAMO (Pertenece a)
    ramos = models.ManyToManyField(Ramo, related_name='ofertas')

    def __str__(self): return self.titulo


#Solicitud Clase: 
class SolicitudClase(models.Model):
    #ID_Solicitud (PK) se crea atomaticamente como 'id'
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

    #Relación N:1 con PERFIL (Solicitante)
    #ID Usuario (Solicitante) (FK)
    solicitante = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='solicitudes_creadas')

    #Relación N:1 con RAMO (Pertenece a)
    ramo = models.ForeignKey(Ramo, on_delete=models.CASCADE, related_name='solicitudes')

    def __str__(self): return self.titulo


#Horario: 
class HorarioOfertado(models.Model):
    #ID_Horario (PK) se crea automaticamente como 'id'
    dia = models.IntegerField(choices=DiaSemana.choices)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    cupos_totales = models.PositiveIntegerField(default=1)

    #Relación N:1 con OFERTA CLASE
    #ID_Oferta (FK)
    oferta = models.ForeignKey(OfertaClase, on_delete=models.CASCADE, related_name='horarios')

    def __str__(self): return f"Horario para {self.oferta.titulo}: {self.hora_inicio} - {self.hora_fin}"



#Perfil-Ramo:
class PerfilRamo(models.Model):
    #ID Usuario (PK)/FK
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    #Id Ramo (PK)/FK
    ramo = models.ForeignKey(Ramo, on_delete=models.CASCADE)

    class Meta: 
        #PK compuesta por ambas FK
        constraints  = [models.UniqueConstraint(fields=['perfil','ramo'], name='unique_perfil_ramo')]
        verbose_name = "Ramo Cursado"
        verbose_name_plural = "Ramos Cursados"

    def __str__(self): return f"{self.perfil.user.username} cursa {self.ramo.name}"

class Inscripcion(models.Model):
    #ID Inscripción (PK) se crea automaticamente como 'id'
    #ID Usuario (Estudiante) (FK) - Relación N:1 con PERFIL
    estudiante = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='inscripciones')

    #ID Horario (FK) - Relación N:1 con HORARIO OFERTADO
    horario_ofertado = models.ForeignKey(HorarioOfertado, on_delete=models.CASCADE, related_name='inscripciones')

    estado = models.IntegerField(
        choices=EstadoInscripcion.choices,
        default=EstadoInscripcion.PENDIENTE,
        verbose_name='Estado de la Inscripción'
    )

    #Atributo
    fecha_reserva = models.DateTimeField(auto_now_add=True)

    def aceptar(self):
        if self.estado != EstadoInscripcion.ACEPTADO:
            self.estado = EstadoInscripcion.ACEPTADO
            self.save()

    def rechazar(self):
        if self.estado != EstadoInscripcion.RECHAZADO:
            self.estado = EstadoInscripcion.RECHAZADO
            self.save()

    class Meta: 
        constraints  = [models.UniqueConstraint(fields=['estudiante', 'horario_ofertado'], name='unique_inscripcion')]
        verbose_name_plural = "Inscripciones"

    def __str__(self): 
        estado_display = EstadoInscripcion(self.estado).label
        return f"Inscripción de {self.estudiante.user.username} a {self.horario_ofertado.oferta.titulo} ({estado_display})"


#Rating:
class Rating(models.Model):
    #ID Rating (PK) se crea automaticamente como 'id'
    valoracion = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    fecha_rating = models.DateTimeField(auto_now_add=True)

    #ID Usuario (CALIFICADOR) (FK) - Relación N:1 con PERFIL
    calificador = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True, related_name='ratings_dados')

    #ID Usuario (CALIFICADO) (FK) - Relación N:1 con PERFIL
    calificado = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='ratings_recibidos')

    #ID Inscripcion (FK) - Relación 1:1 con INSCRPICION (PK es FK)
    #A LO SUMO UN RATING:
    inscripcion = models.OneToOneField(Inscripcion, on_delete=models.CASCADE, related_name='rating')

    def __str__(self): return f"Rating de {self.valoracion} por {self.calificador.user.username}"


#Comentario
class Comentario(models.Model): 
    #ID Comentario (PK) se crea automaticamente como 'id'
    contenido = models.TextField()
    fecha_comentario = models.DateTimeField(auto_now_add = True)

    #ID Usuario (FK) - Relación N:1 con PERFIL (Publicador)
    publicador = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='comentarios_publicados')

    #ID Oferta (FK) - Relación N:1 con OFERTA CLASE
    oferta_clase = models.ForeignKey(OfertaClase, on_delete=models.CASCADE, null=True, blank=True, related_name='comentarios')

    #ID Solicitud (FK) - Relación N:1 con SOLICITUD CLASE
    solicitud_clase = models.ForeignKey(SolicitudClase, on_delete=models.CASCADE, null=True, blank=True, related_name='comentarios')

    def __str__(self): return f"Comentario de {self.publicador} - {self.fecha_comentario.strftime('%Y-%m-%d')}"

