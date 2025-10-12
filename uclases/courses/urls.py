from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('oferta/<int:pk>/', views.oferta_detail, name='oferta_detail'),
    path('solicitud/<int:pk>/', views.solicitud_detail, name='solicitud_detail'),
    path('oferta/nueva/', views.crear_oferta, name='crear_oferta'),
    path('solicitud/nueva/', views.crear_solicitud, name='crear_solicitud'),
    path('oferta/<int:pk>/editar/', views.editar_oferta, name='editar_oferta'),
    path('solicitud/<int:pk>/editar/', views.editar_solicitud, name='editar_solicitud'),
]
