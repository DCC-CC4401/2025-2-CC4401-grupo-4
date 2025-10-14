from django.db import models
from accounts.models import Perfil
from .enums import DiaSemana, EstadoInscripcion
from django.core.validators import MinValueValidator, MaxValueValidator


#Carrera:
class Carrera(models.Model):
    """
    Carrera universitaria.
    
    Representa una carrera profesional (ej: Ingeniería Civil, Física, etc.)
    a la cual pertenecen los usuarios del sistema.
    
    Attributes:
        name (CharField): Nombre de la carrera.
    
    Relationships:
        - Reverse relation: perfil_set (usuarios que estudian esta carrera)
    """
    #ID_Carrera (PK) se crea automaticamente como 'id'
    name = models.CharField(max_length=100)

    class Meta: verbose_name_plural = "Carreras"

    def __str__(self): return self.name

#Ramo:
class Ramo(models.Model):
    """
    Asignatura o materia de estudio universitaria.
    
    Representa un curso o ramo específico (ej: Cálculo I, Física, Programación, etc.).
    
    Attributes:
        name (CharField): Nombre del ramo o asignatura.
    
    Relationships:
        - Reverse relations: ofertas, solicitudes, perfiles_que_cursaron (vía PerfilRamo)
    """
    #ID_Ramo (PK) se crea automaticamente como 'id'
    name = models.CharField(max_length=100)

    def __str__(self): return self.name

#Oferta Clase:
class OfertaClase(models.Model):
    """
    Oferta de clase particular creada por un profesor (usuario).
    
    Representa una publicación donde un usuario ofrece dar clases particulares
    de un ramo específico, con título, descripción y horarios asociados.
    
    Attributes:
        titulo (CharField): Título descriptivo de la oferta.
        descripcion (TextField): Detalles de la oferta.
        fecha_publicacion (DateTimeField): Fecha y hora de creación automática.
        profesor (ForeignKey): Usuario que ofrece la clase.
        ramo (ForeignKey): Asignatura que se ofrece enseñar.
    
    Relationships:
        - ForeignKey a Perfil (profesor que ofrece)
        - ForeignKey a Ramo (asignatura ofrecida)
        - Reverse relation: horarios (horarios disponibles), comentarios
    """
    #ID_Oferta (PK) se crea atomaticamente como 'id'
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

    #Relación N:1 con PERFIL (Profesor)
    #ID Usuario (Profesor) (FK)
    profesor = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name= 'ofertas_creadas')

    #Relación N:1 con RAMO (Pertenece a) - Una oferta es de UN solo ramo
    ramo = models.ForeignKey(Ramo, on_delete=models.CASCADE, related_name='ofertas')

    def __str__(self): return self.titulo


#Solicitud Clase: 
class SolicitudClase(models.Model):
    """
    Solicitud de clase particular creada por un estudiante.
    
    Representa una publicación donde un usuario solicita recibir clases particulares
    de un ramo específico.
    
    Attributes:
        titulo (CharField): Título descriptivo de la solicitud.
        descripcion (TextField): Detalles de la solicitud.
        fecha_publicacion (DateTimeField): Fecha y hora de creación automática.
        solicitante (ForeignKey): Usuario que solicita la clase.
        ramo (ForeignKey): Asignatura.
    
    Relationships:
        - ForeignKey a Perfil (estudiante que solicita)
        - ForeignKey a Ramo (asignatura solicitada)
        - Reverse relation: comentarios
    """
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
    """
    Horario disponible para una oferta de clase particular.
    Se pueden crear multiples horarios por cada oferta.
    
    Define un bloque de tiempo específico en el que el profesor está disponible
    para dar clases, con día de la semana, hora de inicio y fin, y cupos.
    
    Attributes:
        dia (IntegerField): Día de la semana (enum DiaSemana: 1=Lunes, 7=Domingo).
        hora_inicio (TimeField): Hora de inicio del horario.
        hora_fin (TimeField): Hora de finalización del horario.
        cupos_totales (PositiveIntegerField): Cantidad máxima de estudiantes para ese horario.
        oferta (ForeignKey): Oferta de clase a la que pertenece este horario.
    
    Relationships:
        - ForeignKey a OfertaClase (oferta asociada)
        - Reverse relation: inscripciones (estudiantes inscritos)
    """
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
    """
    Tabla intermedia que relaciona usuarios con ramos que han cursado.
    
    Representa la relación many-to-many entre Perfil y Ramo, indicando
    qué asignaturas ha cursado cada usuario en su historial académico.
    
    Attributes:
        perfil (ForeignKey): Usuario que cursó el ramo.
        ramo (ForeignKey): Asignatura que fue cursada.
    
    Relationships:
        - ForeignKey a Perfil
        - ForeignKey a Ramo
    """
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
    """
    Inscripción de un estudiante a un horario específico de una oferta de clase.
    
    Gestiona el ciclo de vida de una reserva de clase, desde la solicitud inicial
    hasta su aceptación, rechazo, cancelación o finalización.
    
    Attributes:
        estudiante (ForeignKey): Usuario que se inscribe a la clase.
        horario_ofertado (ForeignKey): Horario específico al que se inscribe.
        estado (IntegerField): Estado actual (PENDIENTE, ACEPTADO, RECHAZADO, CANCELADO, COMPLETADO).
        fecha_reserva (DateTimeField): Fecha y hora de creación de la inscripción.
    
    Relationships:
        - ForeignKey a Perfil (estudiante inscrito)
        - ForeignKey a HorarioOfertado (horario reservado)
        - Reverse relation: rating (calificación de la clase)
    """
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
        """Acepta una inscripción pendiente, cambiando su estado a ACEPTADO."""
        if self.estado == EstadoInscripcion.PENDIENTE:
            self.estado = EstadoInscripcion.ACEPTADO
            self.save()

    def rechazar(self):
        """Rechaza una inscripción pendiente, cambiando su estado a RECHAZADO."""
        if self.estado == EstadoInscripcion.PENDIENTE:
            self.estado = EstadoInscripcion.RECHAZADO
            self.save()
    
    def cancelar(self):
        """Cancela una inscripción pendiente o aceptada, cambiando su estado a CANCELADO."""
        if ((self.estado == EstadoInscripcion.PENDIENTE) or (self.estado == EstadoInscripcion.ACEPTADO)):
            self.estado = EstadoInscripcion.CANCELADO
            self.save()
    
    def completar(self):
        """Marca una inscripción aceptada como COMPLETADO al finalizar la clase."""
        if self.estado == EstadoInscripcion.ACEPTADO:
            self.estado = EstadoInscripcion.COMPLETADO
            self.save()         
    class Meta: 
        constraints  = [models.UniqueConstraint(fields=['estudiante', 'horario_ofertado'], name='unique_inscripcion')]
        verbose_name_plural = "Inscripciones"

    def __str__(self): 
        estado_display = EstadoInscripcion(self.estado).label
        return f"Inscripción de {self.estudiante.user.username} a {self.horario_ofertado.oferta.titulo} ({estado_display})"


#Rating:
class Rating(models.Model):
    """
    Calificación de una clase completada, dada por un usuario que recibió una clase a otro que dio la clase.

    Permite que un estudiante califique a su profesor después
    de completar una clase, con una valoración de 1 a 5 estrellas.
    
    Attributes:
        valoracion (IntegerField): Puntuación de 1 a 5 estrellas.
        fecha_rating (DateTimeField): Fecha y hora en que se dio la calificación.
        calificador (ForeignKey): Usuario que otorga la calificación.
        calificado (ForeignKey): Usuario que recibe la calificación.
        inscripcion (OneToOneField): Inscripción asociada (solo una calificación por inscripción).
    
    Relationships:
        - ForeignKey a Perfil (calificador)
        - ForeignKey a Perfil (calificado)
        - OneToOneField a Inscripcion (clase calificada)
    """
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
    """
    Comentario publicado en una oferta o solicitud de clase.
    
    Permite a los usuarios hacer preguntas o comentarios sobre ofertas
    o solicitudes de clases particulares. Debe estar asociado a una oferta
    O a una solicitud, pero no a ambas.
    
    Attributes:
        contenido (TextField): Texto del comentario.
        fecha_comentario (DateTimeField): Fecha y hora de publicación automática.
        publicador (ForeignKey): Usuario que publica el comentario.
        oferta_clase (ForeignKey): Oferta en la que se comenta (opcional).
        solicitud_clase (ForeignKey): Solicitud en la que se comenta (opcional).
    
    Relationships:
        - ForeignKey a Perfil (autor del comentario)
        - ForeignKey a OfertaClase (opcional, si comenta en oferta)
        - ForeignKey a SolicitudClase (opcional, si comenta en solicitud)
    
    Note:
        Un comentario debe estar asociado a UNA oferta O UNA solicitud, no ambas.
    """
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

