from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import transaction

from apps.historico.models import Evento
from apps.historico.operacoes import registrar_evento

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    readonly_fields = ("last_login", "date_joined")
    list_display = ("username", "first_name", "last_name", "is_active", "is_staff")

    def has_module_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        # Guardar só nomes de campos, nunca senhas, hashes ou valores pessoais.
        permitidos = {
            "username", "first_name", "last_name", "email", "is_active",
            "is_staff", "is_superuser", "groups", "user_permissions",
        }
        request._kdlab_campos_alterados = sorted(permitidos.intersection(form.changed_data))
        super().save_model(request, obj, form, change)

    def log_addition(self, request, obj, message):
        super().log_addition(request, obj, message)
        registrar_evento(
            ator_id=request.user.pk,
            acao=Evento.Acao.USUARIO_CRIADO,
            alvo_id=obj.pk,
            campos_alterados=request._kdlab_campos_alterados,
        )

    def log_change(self, request, obj, message):
        super().log_change(request, obj, message)
        alteracao_de_senha = request.resolver_match.url_name == "auth_user_password_change"
        registrar_evento(
            ator_id=request.user.pk,
            acao=(
                Evento.Acao.CREDENCIAIS_ALTERADAS if alteracao_de_senha
                else Evento.Acao.USUARIO_ATUALIZADO
            ),
            alvo_id=obj.pk,
            campos_alterados=getattr(request, "_kdlab_campos_alterados", []),
        )

    def user_change_password(self, request, id, form_url=""):
        # O fluxo padrão de senha não é o changeform_view transacional.
        with transaction.atomic():
            return super().user_change_password(request, id, form_url)
