from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator,MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

# Perfil:
class Perfil(models.Model):
    # Relación 1:1 con User basico de Django,
    # user = ID_Usuario (PK)/(FK)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key = True)
    #Atributos de PERFIL:
    telefono = models.CharField(max_length=13, blank=True, null=True)
    descripcion = models.TextField(max_length=500, blank=True)
    foto_url = models.URLField(max_length=200, blank=True, null=True)
    banner_url = models.URLField(max_length=200, blank=True, null=True)
    rating_promedio = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_ratings = models.IntegerField(default=0)
    # Relación N:1 con CARRERA (Una CARRERA es cursada por N Perfiles)
    # ID Carrera (FK)
    carrera = models.ForeignKey('Carrera', on_delete=models.SET_NULL, null=True, blank=True, related_name='perfiles_cursando')

    class Meta: verbose_name_plural = "Perfiles"
    def __str__(self): return f"Perfil de {self.user.username}"

#Automatización de la creación de PERFIL:
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_o_actualizar_perfil(sender, instance, created, **kwargs): 
    if created:
        Perfil.objects.create(user=instance)
    else: 
        try:
            instance.perfil.save()
        except Perfil.DoesNotExist:
            Perfil.objects.create(user=instance)


#Carrera:
class Carrera(models.Model):
    #ID_Carrera (PK) se crea automaticamente como 'id'
    nombre = models.CharField(max_length=100)

    class Meta: verbose_name_plural = "Carreras"

    def __str__(self): return self.nombre

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
    fecha_publicación = models.DateTimeField(auto_now_add=True)

    #Relación N:1 con PERFIL (Solicitante)
    #ID Usuario (Solicitante) (FK)
    solicitante = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='solicitudes_creadas')

    #Relación N:1 con RAMO (Pertenece a)
    ramo = models.ForeignKey(Ramo, on_delete=models.CASCADE, related_name='solicitudes')

    def __str__(self): return self.titulo

#Horario: 
class HorarioOfertado(models.Model):
    #ID_Horario (PK) se crea automaticamente como 'id'
    dia = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(7)]) #Lunes a Viernes
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
        unique_together = ('perfil', 'ramo')
        verbose_name = "Ramo Cursado"
        verbose_name_plural = "Ramos Cursados"

    def __str__(self): return f"{self.perfil.user.username} cursa {self.ramo.nombre}"
#Añadimos a Perfil los ramos cursados.
Perfil.ramos_cursados = models.ManyToManyField(Ramo, through='PerfilRamo', related_name='perfiles_que_cursaron')

class Inscripcion(models.Model):
    #ID Inscripción (PK) se crea automaticamente como 'id'
    #ID Usuario (Estudiante) (FK) - Relación N:1 con PERFIL
    estudiante = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='inscripciones')

    #ID Horario (FK) - Relación N:1 con HORARIO OFERTADO
    horario_ofertado = models.ForeignKey(HorarioOfertado, on_delete=models.CASCADE, related_name='inscripciones')

    #Atributo
    fecha_reserva = models.DateTimeField(auto_now_add=True)

    class Meta: 
        unique_together = ('estudiante', 'horario_ofertado')
        verbose_name_plural = "Inscripciones"

    def __str__(self): return f"Inscripción de {self.estudiante.user.username} a {self.horario_ofertado.oferta.titulo}"

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

