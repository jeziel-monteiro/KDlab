"""Ensaios de banco real para CQ-01, CQ-02 e parte transacional de CQ-05."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from functools import partial
import os
from threading import Barrier
from time import perf_counter

from django.db import IntegrityError, connection, connections, transaction
from django.db.models import Q
from django.test import TransactionTestCase
from django.utils import timezone
from psycopg.types.range import Range

from .models import Evento, Manutencao, MarcadorOperacional, Ocupacao, Recurso, Reserva
from .operacoes import (
    ConflitoDeAgenda,
    FalhaSimulada,
    TransicaoInvalida,
    aprovar,
    cancelar,
    encerrar_manutencao,
    registrar_manutencao,
)


class ProvaAgenda(TransactionTestCase):
    def setUp(self):
        self.inicio = timezone.now() + timedelta(days=1)
        self.fim = self.inicio + timedelta(hours=1)
        self.recurso = Recurso.objects.create(nome="Recurso base")
        self.rodadas = int(os.environ.get("KDLAB_PROVA_RODADAS", "3"))
        self.concorrentes = int(os.environ.get("KDLAB_PROVA_CONCORRENTES", "4"))

    def nova_reserva(self, recurso=None, inicio=None, fim=None):
        return Reserva.objects.create(
            recurso=recurso or self.recurso,
            inicio=inicio or self.inicio,
            fim=fim or self.fim,
        )

    def disputar(self, operacoes):
        barreira = Barrier(len(operacoes), timeout=15)

        def executar(operacao):
            connections.close_all()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT pg_backend_pid()")
                    pid = cursor.fetchone()[0]
                barreira.wait()
                try:
                    return operacao(), pid
                except ConflitoDeAgenda:
                    return "CONFLITO", pid
                except TransicaoInvalida:
                    return "TRANSICAO_INVALIDA", pid
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=len(operacoes)) as executor:
            futuros = [executor.submit(executar, op) for op in operacoes]
            resultados = [f.result(timeout=30) for f in futuros]
        self.assertEqual(len({pid for _, pid in resultados}), len(operacoes))
        return [resultado for resultado, _ in resultados]

    def verificar_integridade(self):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT count(*) FROM agenda_prova_ocupacao a "
                "JOIN agenda_prova_ocupacao b ON a.id < b.id "
                "AND a.recurso_id = b.recurso_id AND a.periodo && b.periodo "
                "WHERE a.ativa AND b.ativa"
            )
            self.assertEqual(cursor.fetchone()[0], 0)
        self.assertFalse(
            Reserva.objects.filter(estado=Reserva.Estado.APROVADA).filter(
                Q(ocupacao__isnull=True) | Q(ocupacao__ativa=False)
            ).exists()
        )
        self.assertFalse(
            Reserva.objects.filter(estado=Reserva.Estado.CANCELADA, ocupacao__ativa=True).exists()
        )

    def test_migracao_instala_extensao_e_exclusao(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT extversion FROM pg_extension WHERE extname = 'btree_gist'")
            self.assertIsNotNone(cursor.fetchone())
            cursor.execute(
                "SELECT contype FROM pg_constraint WHERE conname = 'agenda_sem_sobreposicao' "
                "AND conrelid = 'agenda_prova_ocupacao'::regclass"
            )
            self.assertEqual(cursor.fetchone(), ("x",))

    def test_aprovacoes_concorrentes_distintas(self):
        duracoes = []
        for rodada in range(self.rodadas):
            with self.subTest(rodada=rodada):
                recurso = Recurso.objects.create(nome=f"Disputa {rodada}")
                reservas = [self.nova_reserva(recurso) for _ in range(self.concorrentes)]
                comeco = perf_counter()
                resultados = self.disputar([partial(aprovar, r.pk) for r in reservas])
                duracoes.append(perf_counter() - comeco)
                self.assertEqual(resultados.count("APROVADA"), 1)
                self.assertEqual(resultados.count("CONFLITO"), self.concorrentes - 1)
                self.assertEqual(Reserva.objects.filter(recurso=recurso, estado="PENDENTE").count(), self.concorrentes - 1)
                self.assertEqual(Ocupacao.objects.filter(recurso=recurso, ativa=True).count(), 1)
                self.assertEqual(Evento.objects.filter(acao="APROVACAO", origem_id__in=[r.pk for r in reservas]).count(), 1)
        self.verificar_integridade()
        print(
            f"\nCQ-01: {self.rodadas} rodadas x {self.concorrentes} conexões; "
            f"maior duração da disputa: {max(duracoes):.3f}s; "
            "uma aprovação por rodada; integridade final verificada.",
            flush=True,
        )

    def test_aprovacao_contra_manutencao(self):
        def manter(recurso_id):
            registrar_manutencao(recurso_id, self.inicio, self.fim)
            return "MANUTENCAO"

        for rodada in range(self.rodadas):
            with self.subTest(rodada=rodada):
                recurso = Recurso.objects.create(nome=f"Manutenção {rodada}")
                reserva = self.nova_reserva(recurso)
                resultados = self.disputar([partial(aprovar, reserva.pk), partial(manter, recurso.pk)])
                self.assertEqual(resultados.count("CONFLITO"), 1)
                self.assertEqual(Ocupacao.objects.filter(recurso=recurso, ativa=True).count(), 1)
                reserva.refresh_from_db()
                if "MANUTENCAO" in resultados:
                    self.assertEqual(reserva.estado, "PENDENTE")
                    self.assertEqual(Manutencao.objects.filter(recurso=recurso).count(), 1)
                else:
                    self.assertEqual(reserva.estado, "APROVADA")
                    self.assertFalse(Manutencao.objects.filter(recurso=recurso).exists())
        self.verificar_integridade()

    def test_aprovacao_contra_cancelamento(self):
        for rodada in range(self.rodadas):
            with self.subTest(rodada=rodada):
                recurso = Recurso.objects.create(nome=f"Cancelamento {rodada}")
                reserva = self.nova_reserva(recurso)
                resultados = self.disputar([partial(aprovar, reserva.pk), partial(cancelar, reserva.pk)])
                self.assertIn("CANCELADA", resultados)
                self.assertTrue("APROVADA" in resultados or "TRANSICAO_INVALIDA" in resultados)
                reserva.refresh_from_db()
                self.assertEqual(reserva.estado, "CANCELADA")
                self.assertFalse(Ocupacao.objects.filter(recurso=recurso, ativa=True).exists())
                self.assertEqual(Evento.objects.filter(acao="CANCELAMENTO", origem_id=reserva.pk).count(), 1)
        self.verificar_integridade()

    def test_repeticao_concorrente_da_mesma_aprovacao(self):
        reserva = self.nova_reserva()
        resultados = self.disputar([partial(aprovar, reserva.pk)] * self.concorrentes)
        self.assertEqual(resultados.count("APROVADA"), 1)
        self.assertEqual(resultados.count("JA_APROVADA"), self.concorrentes - 1)
        self.assertEqual(Ocupacao.objects.count(), 1)
        self.assertEqual(Evento.objects.count(), 1)

    def test_exclusao_protege_gravacao_concorrente_sem_lock_da_aplicacao(self):
        def gravar():
            try:
                Ocupacao.objects.create(recurso=self.recurso, tipo="RESERVA", periodo=Range(self.inicio, self.fim, "[)"))
                return "GRAVADA"
            except IntegrityError as erro:
                if erro.__cause__.diag.constraint_name != "agenda_sem_sobreposicao":
                    raise
                return "EXCLUIDA_PELO_BANCO"

        resultados = self.disputar([gravar, gravar])
        self.assertCountEqual(resultados, ["GRAVADA", "EXCLUIDA_PELO_BANCO"])
        self.verificar_integridade()

    def test_pendencias_nao_ocupam_e_manutencao_existente_impede_aprovacao(self):
        a, b = self.nova_reserva(), self.nova_reserva()
        self.assertFalse(Ocupacao.objects.exists())
        registrar_manutencao(self.recurso.pk, self.inicio, self.fim)
        for reserva in (a, b):
            with self.assertRaises(ConflitoDeAgenda):
                aprovar(reserva.pk)
            reserva.refresh_from_db()
            self.assertEqual(reserva.estado, "PENDENTE")
        self.assertEqual(Evento.objects.count(), 1)

    def test_manutencao_nao_cancela_reserva_ja_aprovada(self):
        reserva = self.nova_reserva()
        aprovar(reserva.pk)
        with self.assertRaises(ConflitoDeAgenda):
            registrar_manutencao(self.recurso.pk, self.inicio, self.fim)
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, "APROVADA")
        self.assertFalse(Manutencao.objects.exists())
        self.assertFalse(MarcadorOperacional.objects.exists())
        self.assertEqual(Evento.objects.count(), 1)

    def test_intervalos_adjacentes_e_recursos_diferentes(self):
        a = self.nova_reserva()
        b = self.nova_reserva(inicio=self.fim, fim=self.fim + timedelta(hours=1))
        outro = Recurso.objects.create(nome="Outro recurso")
        c = self.nova_reserva(outro)
        for reserva in (a, b, c):
            self.assertEqual(aprovar(reserva.pk), "APROVADA")
        self.verificar_integridade()

    def test_cancelamento_libera_sem_apagar_historico(self):
        a, b = self.nova_reserva(), self.nova_reserva()
        aprovar(a.pk)
        self.assertEqual(cancelar(a.pk), "CANCELADA")
        self.assertEqual(cancelar(a.pk), "JA_CANCELADA")
        self.assertEqual(aprovar(b.pk), "APROVADA")
        self.assertEqual(Ocupacao.objects.count(), 2)
        self.assertEqual(Ocupacao.objects.filter(ativa=False).count(), 1)
        self.assertEqual(Evento.objects.count(), 3)
        self.verificar_integridade()

    def test_rollback_de_aprovacao_em_tres_pontos(self):
        reserva = self.nova_reserva()
        for etapa in ("apos_ocupacao", "apos_origem", "antes_commit"):
            with self.subTest(etapa=etapa), self.assertRaises(FalhaSimulada):
                aprovar(reserva.pk, falhar_em=etapa)
            reserva.refresh_from_db()
            self.assertEqual(reserva.estado, "PENDENTE")
            self.assertIsNone(reserva.ocupacao_id)
            self.assertFalse(Ocupacao.objects.exists())
            self.assertFalse(Evento.objects.exists())

    def test_rollback_de_manutencao_inclui_marcador(self):
        for etapa in ("apos_origem", "apos_marcador", "antes_commit"):
            with self.subTest(etapa=etapa), self.assertRaises(FalhaSimulada):
                registrar_manutencao(self.recurso.pk, self.inicio, self.fim, falhar_em=etapa)
            self.assertFalse(Manutencao.objects.exists())
            self.assertFalse(Ocupacao.objects.exists())
            self.assertFalse(MarcadorOperacional.objects.exists())
            self.assertFalse(Evento.objects.exists())

    def test_manutencao_vencida_bloqueia_ate_encerramento(self):
        agora = timezone.now()
        manutencao_id = registrar_manutencao(
            self.recurso.pk, agora - timedelta(hours=2), agora - timedelta(hours=1)
        )
        reserva = self.nova_reserva()
        with self.assertRaisesMessage(ConflitoDeAgenda, "vencida"):
            aprovar(reserva.pk)
        self.assertEqual(encerrar_manutencao(manutencao_id), "ENCERRADA")
        self.assertEqual(encerrar_manutencao(manutencao_id), "JA_ENCERRADA")
        self.assertFalse(MarcadorOperacional.objects.filter(encerrado_em__isnull=True).exists())
        self.assertEqual(aprovar(reserva.pk), "APROVADA")
        self.verificar_integridade()

    def test_encerramento_antecipado_reduz_ocupacao(self):
        agora = timezone.now()
        manutencao_id = registrar_manutencao(self.recurso.pk, agora - timedelta(hours=1), self.fim)
        self.assertEqual(encerrar_manutencao(manutencao_id), "ENCERRADA")
        manutencao = Manutencao.objects.select_related("ocupacao").get(pk=manutencao_id)
        self.assertLess(manutencao.ocupacao.periodo.upper, self.inicio)
        self.assertEqual(aprovar(self.nova_reserva().pk), "APROVADA")

    def test_nao_encerra_manutencao_antes_do_inicio(self):
        manutencao_id = registrar_manutencao(self.recurso.pk, self.inicio, self.fim)
        with self.assertRaises(TransicaoInvalida):
            encerrar_manutencao(manutencao_id)
        self.assertEqual(Manutencao.objects.get(pk=manutencao_id).estado, "REGISTRADA")
        self.assertEqual(Evento.objects.count(), 1)

    def test_periodos_invalidos_sao_recusados_pelo_banco(self):
        periodos = [
            "empty",
            f"[{self.inicio.isoformat()},)",
            f"(,{self.fim.isoformat()})",
            f"[{self.inicio.isoformat()},infinity)",
            f"[-infinity,{self.fim.isoformat()})",
            f"[{self.inicio.isoformat()},{self.fim.isoformat()}]",
            f"({self.inicio.isoformat()},{self.fim.isoformat()})",
        ]
        for periodo in periodos:
            with self.subTest(periodo=periodo), self.assertRaises(IntegrityError), transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO agenda_prova_ocupacao (recurso_id, tipo, periodo, ativa) "
                        "VALUES (%s, 'RESERVA', %s::tstzrange, true)",
                        [self.recurso.pk, periodo],
                    )
        self.assertFalse(Ocupacao.objects.exists())

    def test_recurso_inativo_nao_aprova(self):
        reserva = self.nova_reserva()
        Recurso.objects.filter(pk=self.recurso.pk).update(ativo=False)
        with self.assertRaisesMessage(ConflitoDeAgenda, "inativo"):
            aprovar(reserva.pk)
        self.assertFalse(Ocupacao.objects.exists())
        self.assertFalse(Evento.objects.exists())
