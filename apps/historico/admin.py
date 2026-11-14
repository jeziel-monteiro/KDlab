from django.contrib import admin

from .models import Evento


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ("instante", "acao", "ator_id", "tipo_alvo", "alvo_id", "resultado")
    list_filter = ("acao",)
    readonly_fields = (
        "ator_id", "acao", "tipo_alvo", "alvo_id", "resultado", "campos_alterados", "instante",
    )

    def has_module_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
