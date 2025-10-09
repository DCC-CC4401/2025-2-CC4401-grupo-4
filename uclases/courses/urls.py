from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('oferta/<int:pk>/', views.oferta_detail, name='oferta_detail'),
    path('solicitud/<int:pk>/', views.solicitud_detail, name='solicitud_detail'),
]
