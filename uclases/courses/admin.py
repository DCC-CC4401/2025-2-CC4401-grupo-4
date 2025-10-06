from django.contrib import admin
from .models import (
    Carrera, Ramo, OfertaClase, SolicitudClase, 
    HorarioOfertado, PerfilRamo, Inscripcion, Rating, Comentario
)

@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    """Admin para el modelo Carrera"""
    list_display = ("id", "name", "total_perfiles")
    search_fields = ("name",)
    ordering = ("name",)
    
    def total_perfiles(self, obj):
        """Contar cuántos perfiles tienen esta carrera"""
        return obj.perfiles_cursando.count()
    total_perfiles.short_description = "Total Estudiantes"

@admin.register(Ramo)
class RamoAdmin(admin.ModelAdmin):
    """Admin para el modelo Ramo"""
    list_display = ("id", "name", "total_ofertas", "total_solicitudes")
    search_fields = ("name",)
    ordering = ("name",)
    
    def total_ofertas(self, obj):
        return obj.ofertas.count()
    total_ofertas.short_description = "Ofertas"
    
    def total_solicitudes(self, obj):
        return obj.solicitudes.count()
    total_solicitudes.short_description = "Solicitudes"

class HorarioOfertadoInline(admin.TabularInline):
    """Inline para gestionar horarios desde OfertaClase"""
    model = HorarioOfertado
    extra = 1
    fields = ("dia", "hora_inicio", "hora_fin", "cupos_totales")

@admin.register(OfertaClase)
class OfertaClaseAdmin(admin.ModelAdmin):
    """Admin para el modelo OfertaClase"""
    list_display = ("id", "titulo", "profesor", "fecha_publicacion", "total_horarios", "total_comentarios")
    search_fields = ("titulo", "descripcion", "profesor__user__username")
    list_filter = ("fecha_publicacion",)
    ordering = ("-fecha_publicacion",)
    filter_horizontal = ("ramos",)
    
    fieldsets = (
        ("Información Básica", {"fields": ("titulo", "descripcion", "profesor")}),
        ("Ramos", {"fields": ("ramos",)}),
        ("Fechas", {"fields": ("fecha_publicacion",)}),
    )
    
    readonly_fields = ("fecha_publicacion",)
    inlines = [HorarioOfertadoInline]
    
    def total_horarios(self, obj):
        return obj.horarios.count()
    total_horarios.short_description = "Horarios"
    
    def total_comentarios(self, obj):
        return obj.comentarios.count()
    total_comentarios.short_description = "Comentarios"

@admin.register(SolicitudClase)
class SolicitudClaseAdmin(admin.ModelAdmin):
    """Admin para el modelo SolicitudClase"""
    list_display = ("id", "titulo", "solicitante", "ramo", "fecha_publicacion", "total_comentarios")
    search_fields = ("titulo", "descripcion", "solicitante__user__username")
    list_filter = ("fecha_publicacion", "ramo")
    ordering = ("-fecha_publicacion",)
    
    fieldsets = (
        ("Información Básica", {"fields": ("titulo", "descripcion", "solicitante", "ramo")}),
        ("Fechas", {"fields": ("fecha_publicacion",)}),
    )
    
    readonly_fields = ("fecha_publicacion",)
    
    def total_comentarios(self, obj):
        return obj.comentarios.count()
    total_comentarios.short_description = "Comentarios"

@admin.register(HorarioOfertado)
class HorarioOfertadoAdmin(admin.ModelAdmin):
    """Admin para el modelo HorarioOfertado"""
    list_display = ("id", "oferta", "dia", "hora_inicio", "hora_fin", "cupos_totales", "cupos_ocupados")
    search_fields = ("oferta__titulo",)
    list_filter = ("dia", "oferta")
    ordering = ("dia", "hora_inicio")
    
    def cupos_ocupados(self, obj):
        return obj.inscripciones.count()
    cupos_ocupados.short_description = "Ocupados"

@admin.register(PerfilRamo)
class PerfilRamoAdmin(admin.ModelAdmin):
    """Admin para el modelo PerfilRamo (Ramos Cursados)"""
    list_display = ("id", "perfil", "ramo")
    search_fields = ("perfil__user__username", "ramo__name")
    list_filter = ("ramo",)
    ordering = ("perfil", "ramo")

@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    """Admin para el modelo Inscripcion"""
    list_display = ("id", "estudiante", "get_oferta", "get_horario", "fecha_reserva", "tiene_rating")
    search_fields = ("estudiante__user__username", "horario_ofertado__oferta__titulo")
    list_filter = ("fecha_reserva",)
    ordering = ("-fecha_reserva",)
    
    readonly_fields = ("fecha_reserva",)
    
    def get_oferta(self, obj):
        return obj.horario_ofertado.oferta.titulo
    get_oferta.short_description = "Oferta"
    
    def get_horario(self, obj):
        return f"{obj.horario_ofertado.get_dia_display()} {obj.horario_ofertado.hora_inicio}"
    get_horario.short_description = "Horario"
    
    def tiene_rating(self, obj):
        return hasattr(obj, 'rating')
    tiene_rating.boolean = True
    tiene_rating.short_description = "¿Rating?"

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Admin para el modelo Rating"""
    list_display = ("id", "calificador", "calificado", "valoracion", "fecha_rating", "get_oferta")
    search_fields = ("calificador__user__username", "calificado__user__username")
    list_filter = ("valoracion", "fecha_rating")
    ordering = ("-fecha_rating",)
    
    readonly_fields = ("fecha_rating",)
    
    def get_oferta(self, obj):
        return obj.inscripcion.horario_ofertado.oferta.titulo
    get_oferta.short_description = "Oferta"

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    """Admin para el modelo Comentario"""
    list_display = ("id", "publicador", "get_tipo", "get_destino", "fecha_comentario")
    search_fields = ("publicador__user__username", "contenido")
    list_filter = ("fecha_comentario",)
    ordering = ("-fecha_comentario",)
    
    readonly_fields = ("fecha_comentario",)
    
    fieldsets = (
        ("Autor", {"fields": ("publicador",)}),
        ("Contenido", {"fields": ("contenido",)}),
        ("Destino", {"fields": ("oferta_clase", "solicitud_clase")}),
        ("Fechas", {"fields": ("fecha_comentario",)}),
    )
    
    def get_tipo(self, obj):
        if obj.oferta_clase:
            return "Oferta"
        elif obj.solicitud_clase:
            return "Solicitud"
        return "N/A"
    get_tipo.short_description = "Tipo"
    
    def get_destino(self, obj):
        if obj.oferta_clase:
            return obj.oferta_clase.titulo
        elif obj.solicitud_clase:
            return obj.solicitud_clase.titulo
        return "N/A"
    get_destino.short_description = "Publicación"
