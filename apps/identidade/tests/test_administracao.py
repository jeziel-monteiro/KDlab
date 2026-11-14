import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from apps.historico.models import Evento

from .test_acesso import SENHA_TESTE


Usuario = get_user_model()


class AdministracaoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.administrador = Usuario.objects.create_superuser(username="admin", password=SENHA_TESTE)
        cls.usuario = Usuario.objects.create_user(username="professor", password=SENHA_TESTE)
        cls.adicionar = reverse("admin:identidade_usuario_add")
        cls.listar = reverse("admin:identidade_usuario_changelist")

    def dados_nova_conta(self):
        return {
            "username": "nova_aluna", "usable_password": "true",
            "password1": SENHA_TESTE, "password2": SENHA_TESTE, "_save": "Salvar",
        }

    def test_somente_superusuario_tecnico_provisiona_contas(self):
        self.client.force_login(self.administrador)
        resposta = self.client.post(self.adicionar, self.dados_nova_conta())
        self.assertEqual(resposta.status_code, 302)
        nova = Usuario.objects.get(username="nova_aluna")
        self.assertTrue(nova.check_password(SENHA_TESTE))
        self.assertNotEqual(nova.password, SENHA_TESTE)
        self.assertFalse(nova.is_staff)
        self.assertFalse(nova.is_superuser)
        evento = Evento.objects.get()
        self.assertEqual(evento.acao, Evento.Acao.USUARIO_CRIADO)
        self.assertEqual(evento.ator_id, self.administrador.pk)
        self.assertEqual(evento.alvo_id, nova.pk)
        serializado = json.dumps(list(Evento.objects.values()), default=str)
        self.assertNotIn(SENHA_TESTE, serializado)
        self.assertNotIn(nova.password, serializado)

    def test_usuario_comum_nao_provisiona_nem_consulta_contas_alheias(self):
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get(self.listar).status_code, 302)
        self.assertEqual(self.client.post(self.adicionar, self.dados_nova_conta()).status_code, 302)
        self.assertFalse(Usuario.objects.filter(username="nova_aluna").exists())
        self.assertFalse(Evento.objects.exists())

    def test_staff_com_permissoes_genericas_nao_pode_escalar_privilegios(self):
        self.usuario.is_staff = True
        self.usuario.save(update_fields=["is_staff"])
        self.usuario.user_permissions.add(*Permission.objects.filter(
            content_type__app_label="identidade", codename__in=["add_usuario", "change_usuario", "view_usuario"],
        ))
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get(self.listar).status_code, 302)
        dados = {**self.dados_nova_conta(), "is_superuser": "on", "is_staff": "on"}
        self.assertEqual(self.client.post(self.adicionar, dados).status_code, 302)
        self.assertFalse(Usuario.objects.filter(username="nova_aluna").exists())

    def test_inativacao_administrativa_e_auditada(self):
        self.client.force_login(self.administrador)
        editar = reverse("admin:identidade_usuario_change", args=[self.usuario.pk])
        resposta = self.client.post(editar, {
            "username": self.usuario.username, "first_name": "Professor", "last_name": "",
            "email": "", "groups": [], "user_permissions": [], "_save": "Salvar",
        })
        self.assertEqual(resposta.status_code, 302)
        self.usuario.refresh_from_db()
        self.assertFalse(self.usuario.is_active)
        evento = Evento.objects.get(acao=Evento.Acao.USUARIO_ATUALIZADO)
        self.assertIn("is_active", evento.campos_alterados)

    def test_alteracao_de_credenciais_e_auditada_sem_senha(self):
        self.client.force_login(self.administrador)
        url = reverse("admin:auth_user_password_change", args=[self.usuario.pk])
        nova_senha = "Outra-Senha-Ficticia-2026!"
        resposta = self.client.post(url, {
            "password1": nova_senha, "password2": nova_senha, "usable_password": "true",
        })
        self.assertEqual(resposta.status_code, 302)
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.check_password(nova_senha))
        evento = Evento.objects.get(acao=Evento.Acao.CREDENCIAIS_ALTERADAS)
        self.assertEqual(evento.ator_id, self.administrador.pk)
        self.assertEqual(evento.campos_alterados, [])

    def test_usuario_e_inativado_em_vez_de_excluido(self):
        self.client.force_login(self.administrador)
        url = reverse("admin:identidade_usuario_delete", args=[self.usuario.pk])
        self.assertEqual(self.client.post(url, {"post": "yes"}).status_code, 403)
        self.assertTrue(Usuario.objects.filter(pk=self.usuario.pk).exists())

    def test_falha_no_historico_reverte_o_provisionamento(self):
        self.client.force_login(self.administrador)
        with patch("apps.identidade.admin.registrar_evento", side_effect=RuntimeError("Falha simulada")):
            with self.assertRaisesMessage(RuntimeError, "Falha simulada"):
                self.client.post(self.adicionar, self.dados_nova_conta())
        self.assertFalse(Usuario.objects.filter(username="nova_aluna").exists())
        self.assertFalse(Evento.objects.exists())

    def test_falha_no_historico_reverte_alteracao_de_senha(self):
        self.client.force_login(self.administrador)
        url = reverse("admin:auth_user_password_change", args=[self.usuario.pk])
        with patch("apps.identidade.admin.registrar_evento", side_effect=RuntimeError("Falha simulada")):
            with self.assertRaisesMessage(RuntimeError, "Falha simulada"):
                self.client.post(url, {
                    "password1": "Outra-Senha-Ficticia-2026!",
                    "password2": "Outra-Senha-Ficticia-2026!", "usable_password": "true",
                })
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.check_password(SENHA_TESTE))
        self.assertFalse(Evento.objects.exists())

    def test_troca_de_senha_propria_no_painel_tambem_e_auditada(self):
        self.client.force_login(self.administrador)
        resposta = self.client.post(reverse("admin:password_change"), {
            "old_password": SENHA_TESTE,
            "new_password1": "Outra-Senha-Ficticia-2026!",
            "new_password2": "Outra-Senha-Ficticia-2026!",
        })
        self.assertEqual(resposta.status_code, 302)
        evento = Evento.objects.get(acao=Evento.Acao.CREDENCIAIS_ALTERADAS)
        self.assertEqual(evento.ator_id, self.administrador.pk)
        self.assertEqual(evento.alvo_id, self.administrador.pk)

    def test_falha_no_historico_reverte_troca_de_senha_propria(self):
        self.client.force_login(self.administrador)
        with patch("kdlab.admin.registrar_evento", side_effect=RuntimeError("Falha simulada")):
            with self.assertRaisesMessage(RuntimeError, "Falha simulada"):
                self.client.post(reverse("admin:password_change"), {
                    "old_password": SENHA_TESTE,
                    "new_password1": "Outra-Senha-Ficticia-2026!",
                    "new_password2": "Outra-Senha-Ficticia-2026!",
                })
        self.administrador.refresh_from_db()
        self.assertTrue(self.administrador.check_password(SENHA_TESTE))
        self.assertFalse(Evento.objects.exists())
