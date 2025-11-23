from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notifications_view, name='list'),
    path('<int:notification_id>/mark-read/', views.mark_as_read, name='mark_read'),
    path('<int:notification_id>/mark-unread/', views.mark_as_unread, name='mark_unread'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_read'),
]
