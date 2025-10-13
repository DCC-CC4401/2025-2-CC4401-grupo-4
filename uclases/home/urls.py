from django.urls import path

from .views import home, perfil_autocomplete_api


app_name = "home"


urlpatterns = [
    path("", home, name="home"),
    path("api/perfiles/", perfil_autocomplete_api, name="perfil-autocomplete-api"),
]
