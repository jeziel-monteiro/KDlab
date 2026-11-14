"""Só coordenação transacional. Não implementa a autorização do produto."""

from django.db import IntegrityError, transaction
from django.utils import timezone
from psycopg.types.range import Range

from .models import Evento, Manutencao, MarcadorOperacional, Ocupacao, Recurso, Reserva


class ConflitoDeAgenda(Exception):
    pass


class TransicaoInvalida(Exception):
    pass


class FalhaSimulada(Exception):
    pass


def _falhar(etapa, falhar_em):
    if etapa == falhar_em:
        raise FalhaSimulada(etapa)


def _periodo(inicio, fim):
    if timezone.is_naive(inicio) or timezone.is_naive(fim) or inicio >= fim:
        raise ValueError("O período deve ter instantes com fuso e início anterior ao fim.")
    return Range(inicio, fim, "[)")


def _verificar_disponibilidade(recurso, periodo):
    if not recurso.ativo:
        raise ConflitoDeAgenda("Recurso inativo.")
    if MarcadorOperacional.objects.filter(
        ocupacao__recurso=recurso, encerrado_em__isnull=True, prazo__lte=timezone.now()
    ).exists():
        raise ConflitoDeAgenda("Manutenção vencida sem encerramento.")
    if Ocupacao.objects.filter(recurso=recurso, ativa=True, periodo__overlap=periodo).exists():
        raise ConflitoDeAgenda("Período ocupado.")


def _traduzir_conflito(erro):
    causa = erro.__cause__
    if causa is not None and causa.diag.constraint_name == "agenda_sem_sobreposicao":
        raise ConflitoDeAgenda("Período ocupado.") from erro
    raise erro


def aprovar(reserva_id, *, falhar_em=None):
    try:
        with transaction.atomic():
            recurso_id = Reserva.objects.values_list("recurso_id", flat=True).get(pk=reserva_id)
            recurso = Recurso.objects.select_for_update().get(pk=recurso_id)
            reserva = Reserva.objects.select_for_update().get(pk=reserva_id)
            if reserva.estado == Reserva.Estado.APROVADA:
                return "JA_APROVADA"
            if reserva.estado != Reserva.Estado.PENDENTE:
                raise TransicaoInvalida(reserva.estado)
            periodo = _periodo(reserva.inicio, reserva.fim)
            _verificar_disponibilidade(recurso, periodo)
            ocupacao = Ocupacao.objects.create(
                recurso=recurso, tipo=Ocupacao.Tipo.RESERVA, periodo=periodo
            )
            _falhar("apos_ocupacao", falhar_em)
            reserva.estado = Reserva.Estado.APROVADA
            reserva.ocupacao = ocupacao
            reserva.save(update_fields=["estado", "ocupacao"])
            _falhar("apos_origem", falhar_em)
            Evento.objects.create(acao="APROVACAO", origem="RESERVA", origem_id=reserva.pk)
            _falhar("antes_commit", falhar_em)
        return "APROVADA"
    except IntegrityError as erro:
        _traduzir_conflito(erro)


def cancelar(reserva_id):
    with transaction.atomic():
        recurso_id = Reserva.objects.values_list("recurso_id", flat=True).get(pk=reserva_id)
        Recurso.objects.select_for_update().get(pk=recurso_id)
        reserva = Reserva.objects.select_for_update().get(pk=reserva_id)
        if reserva.estado == Reserva.Estado.CANCELADA:
            return "JA_CANCELADA"
        if reserva.ocupacao_id:
            Ocupacao.objects.filter(pk=reserva.ocupacao_id).update(ativa=False)
        reserva.estado = Reserva.Estado.CANCELADA
        reserva.save(update_fields=["estado"])
        Evento.objects.create(acao="CANCELAMENTO", origem="RESERVA", origem_id=reserva.pk)
    return "CANCELADA"


def registrar_manutencao(recurso_id, inicio, fim, *, falhar_em=None):
    periodo = _periodo(inicio, fim)
    try:
        with transaction.atomic():
            recurso = Recurso.objects.select_for_update().get(pk=recurso_id)
            _verificar_disponibilidade(recurso, periodo)
            ocupacao = Ocupacao.objects.create(
                recurso=recurso, tipo=Ocupacao.Tipo.MANUTENCAO, periodo=periodo
            )
            manutencao = Manutencao.objects.create(recurso=recurso, ocupacao=ocupacao)
            _falhar("apos_origem", falhar_em)
            MarcadorOperacional.objects.create(ocupacao=ocupacao, prazo=fim)
            _falhar("apos_marcador", falhar_em)
            Evento.objects.create(acao="BLOQUEIO", origem="MANUTENCAO", origem_id=manutencao.pk)
            _falhar("antes_commit", falhar_em)
        return manutencao.pk
    except IntegrityError as erro:
        _traduzir_conflito(erro)


def encerrar_manutencao(manutencao_id):
    with transaction.atomic():
        recurso_id = Manutencao.objects.values_list("recurso_id", flat=True).get(pk=manutencao_id)
        Recurso.objects.select_for_update().get(pk=recurso_id)
        manutencao = Manutencao.objects.select_for_update().get(pk=manutencao_id)
        if manutencao.estado == Manutencao.Estado.ENCERRADA:
            return "JA_ENCERRADA"
        ocupacao = Ocupacao.objects.get(pk=manutencao.ocupacao_id)
        agora = timezone.now()
        if agora <= ocupacao.periodo.lower:
            raise TransicaoInvalida("Manutenção ainda não iniciou.")
        if agora < ocupacao.periodo.upper:
            ocupacao.periodo = _periodo(ocupacao.periodo.lower, agora)
            ocupacao.save(update_fields=["periodo"])
        manutencao.estado = Manutencao.Estado.ENCERRADA
        manutencao.save(update_fields=["estado"])
        MarcadorOperacional.objects.filter(ocupacao=ocupacao).update(encerrado_em=agora)
        Evento.objects.create(acao="ENCERRAMENTO", origem="MANUTENCAO", origem_id=manutencao.pk)
    return "ENCERRADA"
