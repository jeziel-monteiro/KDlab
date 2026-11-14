from django.db import models


class Evento(models.Model):
    class Acao(models.TextChoices):
        USUARIO_CRIADO = "USUARIO_CRIADO", "Usuário criado"
        USUARIO_ATUALIZADO = "USUARIO_ATUALIZADO", "Usuário atualizado"
        CREDENCIAIS_ALTERADAS = "CREDENCIAIS_ALTERADAS", "Credenciais alteradas"

    # Identificadores preservam a independência do módulo de domínio.
    ator_id = models.PositiveBigIntegerField("identificador do ator")
    acao = models.CharField("ação", max_length=32, choices=Acao.choices)
    tipo_alvo = models.CharField("tipo de registro", max_length=24, default="usuario")
    alvo_id = models.PositiveBigIntegerField("identificador do registro")
    resultado = models.CharField(max_length=12, default="SUCESSO", editable=False)
    campos_alterados = models.JSONField("campos alterados", default=list)
    instante = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-instante", "-pk")
        verbose_name = "evento"
        verbose_name_plural = "eventos"

    def __str__(self):
        return f"{self.get_acao_display()} · {self.tipo_alvo} #{self.alvo_id}"
