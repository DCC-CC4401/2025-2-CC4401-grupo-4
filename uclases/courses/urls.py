from django.urls import path

from . import views

app_name = 'courses'

urlpatterns = [
    path('publications/', views.publications_view, name='publications'),
    path('publications/offer/<int:pk>/', views.oferta_detail, name='oferta_detail'),
    path('publications/request/<int:pk>/', views.solicitud_detail, name='solicitud_detail'),
    path('oferta/nueva/', views.crear_oferta, name='crear_oferta'),
    path('solicitud/nueva/', views.crear_solicitud, name='crear_solicitud'),
    path('oferta/<int:pk>/editar/', views.editar_oferta, name='editar_oferta'),
    path('solicitud/<int:pk>/editar/', views.editar_solicitud, name='editar_solicitud'),
    path('publications/offer/<int:pk>/inscribirse/',  views.inscribirse_view, name='inscribirse'),
    
    # Gestión de inscripciones
    path('mis-inscripciones/', views.mis_inscripciones_view, name='mis_inscripciones'),
    path('inscripcion/<int:pk>/aceptar/', views.aceptar_inscripcion, name='aceptar_inscripcion'),
    path('inscripcion/<int:pk>/rechazar/', views.rechazar_inscripcion, name='rechazar_inscripcion'),
    path('inscripcion/<int:pk>/cancelar/', views.cancelar_inscripcion, name='cancelar_inscripcion'),

    # Gestión de propuesta de clases
    path('proponer/<int:solicitud_id>/', views.proponer_oferta_clase, name='proponer_oferta'),

    # Gestión de clases para profesores
    path('horario/<int:pk>/completar/', views.completar_horario_view, name='completar_horario'),
    
    # Ratings
    path('rating/crear/', views.crear_rating_view, name='crear_rating'),

    
    #dashboard mis publis
    path('mis-ofertas/', views.dashboard_mis_ofertas, name='mis_ofertas'),
    path('mis-ofertas/<int:oferta_id>/', views.mis_ofertas_horarios_view, name='mis_ofertas_horarios'),
    path('mis-solicitudes/', views.dashboard_mis_solicitudes, name='mis_solicitudes'),
    path('eliminar-oferta/<int:oferta_id>/', views.eliminar_oferta, name='eliminar_oferta'),
]
