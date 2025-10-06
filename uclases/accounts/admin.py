from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Perfil

class PerfilInline(admin.StackedInline):
    """Inline para editar el Perfil desde el User"""
    model = Perfil
    can_delete = False
    verbose_name = "Perfil"
    verbose_name_plural = "Perfil"
    fk_name = 'user'
    fields = ('telefono', 'descripcion', 'foto_url', 'banner_url', 'carrera', 'rating_promedio', 'total_ratings')
    readonly_fields = ('rating_promedio', 'total_ratings')

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin personalizado para el modelo User"""
    # Columnas en el listado
    list_display = ("id", "username", "email", "public_uid", "is_active", "is_staff", "date_joined")
    search_fields = ("username", "email", "public_uid")
    list_filter = ("is_staff", "is_superuser", "is_active", "date_joined")
    ordering = ("-date_joined",)

    # Secciones del formulario al editar
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Información Personal"), {"fields": ("first_name", "last_name", "email")}),
        (_("Campos Extra"), {"fields": ("public_uid",)}),
        (_("Permisos"), {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
        (_("Fechas Importantes"), {"fields": ("last_login", "date_joined")}),
    )
    
    readonly_fields = ("public_uid", "date_joined", "last_login")

    # Secciones del formulario al crear
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2"),
        }),
    )

    inlines = [PerfilInline]

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    """Admin para el modelo Perfil"""
    list_display = ("user", "get_email", "telefono", "carrera", "rating_promedio", "total_ratings")
    search_fields = ("user__username", "user__email", "telefono")
    list_filter = ("carrera", "rating_promedio")
    ordering = ("-rating_promedio",)
    
    fieldsets = (
        ("Usuario", {"fields": ("user",)}),
        ("Información Personal", {"fields": ("telefono", "descripcion", "carrera")}),
        ("Imágenes", {"fields": ("foto_url", "banner_url")}),
        ("Rating", {"fields": ("rating_promedio", "total_ratings")}),
    )
    
    readonly_fields = ("rating_promedio", "total_ratings")
    
    def get_email(self, obj):
        """Obtener el email del usuario relacionado"""
        return obj.user.email
    get_email.short_description = "Email"