from django.contrib.auth import views
from django.urls import path
from .views import signin_view, signup_view, logout_view

app_name = 'accounts'

urlpatterns = [
    path('login/', signin_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', signup_view, name='register'),]