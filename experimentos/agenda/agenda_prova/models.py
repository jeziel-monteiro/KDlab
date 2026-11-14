"""Modelo descartável para verificar a integridade, sem perfis ou interface."""

from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField, RangeOperators
from django.db import models
from django.db.models import F, Q


def limite_finito(limite):
    return models.Func(
        models.Func(F("periodo"), function=limite, output_field=models.DateTimeField()),
        function="isfinite",
        output_field=models.BooleanField(),
    )


class Recurso(models.Model):
    nome = models.CharField(max_length=120, unique=True)
    ativo = models.BooleanField(default=True)


class Ocupacao(models.Model):
    class Tipo(models.TextChoices):
        RESERVA = "RESERVA"
        MANUTENCAO = "MANUTENCAO"

    recurso = models.ForeignKey(Recurso, on_delete=models.PROTECT)
    tipo = models.CharField(max_length=12, choices=Tipo.choices)
    periodo = DateTimeRangeField()
    ativa = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="agenda_periodo_finito_semiaberto",
                condition=(
                    Q(
                        periodo__isempty=False,
                        periodo__lower_inc=True,
                        periodo__upper_inc=False,
                        periodo__lower_inf=False,
                        periodo__upper_inf=False,
                    )
                    & limite_finito("lower")
                    & limite_finito("upper")
                ),
            ),
            ExclusionConstraint(
                name="agenda_sem_sobreposicao",
                expressions=[
                    ("recurso", RangeOperators.EQUAL),
                    ("periodo", RangeOperators.OVERLAPS),
                ],
                condition=Q(ativa=True),
            ),
        ]


class Reserva(models.Model):
    class Estado(models.TextChoices):
        PENDENTE = "PENDENTE"
        APROVADA = "APROVADA"
        CANCELADA = "CANCELADA"

    recurso = models.ForeignKey(Recurso, on_delete=models.PROTECT)
    inicio = models.DateTimeField()
    fim = models.DateTimeField()
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.PENDENTE)
    ocupacao = models.OneToOneField(
        Ocupacao, null=True, on_delete=models.PROTECT, related_name="reserva"
    )

    class Meta:
        constraints = [
            models.CheckConstraint(name="reserva_inicio_antes_fim", condition=Q(inicio__lt=F("fim")))
        ]


class Manutencao(models.Model):
    class Estado(models.TextChoices):
        REGISTRADA = "REGISTRADA"
        ENCERRADA = "ENCERRADA"

    recurso = models.ForeignKey(Recurso, on_delete=models.PROTECT)
    ocupacao = models.OneToOneField(Ocupacao, on_delete=models.PROTECT)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.REGISTRADA)


class MarcadorOperacional(models.Model):
    ocupacao = models.OneToOneField(Ocupacao, on_delete=models.PROTECT)
    prazo = models.DateTimeField()
    encerrado_em = models.DateTimeField(null=True)


class Evento(models.Model):
    acao = models.CharField(max_length=40)
    origem = models.CharField(max_length=12)
    origem_id = models.BigIntegerField()
    instante = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["acao", "origem", "origem_id"], name="evento_sucesso_unico_na_prova"
            )
        ]
