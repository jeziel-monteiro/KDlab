from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Evento


class ConsultaHistoricoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = get_user_model().objects.create_superuser(username="admin", password="Senha-Ficticia-2026!")
        cls.usuario = get_user_model().objects.create_user(username="aluno")
        cls.evento = Evento.objects.create(
            ator_id=cls.admin.pk, alvo_id=cls.usuario.pk, acao=Evento.Acao.USUARIO_CRIADO,
        )

    def test_superusuario_consulta_eventos(self):
        self.client.force_login(self.admin)
        resposta = self.client.get(reverse("admin:historico_evento_changelist"))
        self.assertContains(resposta, "Usuário criado")

    def test_evento_nao_pode_ser_criado_editado_ou_excluido_pelo_admin(self):
        self.client.force_login(self.admin)
        urls = [
            reverse("admin:historico_evento_add"),
            reverse("admin:historico_evento_change", args=[self.evento.pk]),
            reverse("admin:historico_evento_delete", args=[self.evento.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.post(url, {"post": "yes", "acao": "ALTERADA"}).status_code, 403)
        self.evento.refresh_from_db()
        self.assertEqual(self.evento.acao, Evento.Acao.USUARIO_CRIADO)
        self.assertEqual(Evento.objects.count(), 1)

    def test_usuario_comum_nao_consulta_historico_global(self):
        self.client.force_login(self.usuario)
        resposta = self.client.get(reverse("admin:historico_evento_changelist"))
        self.assertEqual(resposta.status_code, 302)
