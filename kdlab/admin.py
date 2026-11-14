from django.contrib.admin import AdminSite
from django.db import transaction

from apps.historico.models import Evento
from apps.historico.operacoes import registrar_evento


class AdministracaoSite(AdminSite):
    def has_permission(self, request):
        # O painel é técnico; perfis do produto não equivalem a superusuário.
        return super().has_permission(request) and request.user.is_superuser

    def password_change(self, request, extra_context=None):
        with transaction.atomic():
            resposta = super().password_change(request, extra_context)
            if request.method == "POST" and resposta.status_code == 302:
                registrar_evento(
                    ator_id=request.user.pk,
                    acao=Evento.Acao.CREDENCIAIS_ALTERADAS,
                    alvo_id=request.user.pk,
                )
            return resposta
