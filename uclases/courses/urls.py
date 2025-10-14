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

]
