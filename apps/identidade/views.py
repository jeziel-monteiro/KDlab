from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from .forms import FormularioEntrada


class EntradaView(LoginView):
    authentication_form = FormularioEntrada
    template_name = "identidade/entrar.html"
    redirect_authenticated_user = True


@never_cache
@login_required
def inicio(request):
    return render(request, "identidade/inicio.html")
