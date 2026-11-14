from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import EntradaView


app_name = "identidade"
urlpatterns = [
    path("entrar/", EntradaView.as_view(), name="entrar"),
    path("sair/", LogoutView.as_view(), name="sair"),
]
