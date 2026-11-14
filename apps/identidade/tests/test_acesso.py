from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


Usuario = get_user_model()
SENHA_TESTE = "Acesso-Ficticio-2026!"


class AcessoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = Usuario.objects.create_user(
            username="aluna", password=SENHA_TESTE, first_name="Ana",
        )
        cls.entrar = reverse("identidade:entrar")
        cls.sair = reverse("identidade:sair")

    def test_inicio_exige_sessao(self):
        resposta = self.client.get(reverse("inicio"))
        self.assertRedirects(resposta, self.entrar + "?next=/")

    def test_login_e_consulta_dos_dados_proprios(self):
        resposta = self.client.post(self.entrar, {"username": "aluna", "password": SENHA_TESTE})
        self.assertRedirects(resposta, reverse("inicio"))
        self.assertEqual(self.client.session["_auth_user_id"], str(self.usuario.pk))
        pagina = self.client.get(reverse("inicio"))
        self.assertContains(pagina, "Olá, Ana")
        self.assertContains(pagina, "Acesso ativo")
        self.assertNotContains(pagina, "Gerenciar usuários")
        self.assertIn("no-store", pagina.headers["Cache-Control"])

    def test_senha_errada_nao_inicia_sessao(self):
        resposta = self.client.post(self.entrar, {"username": "aluna", "password": "incorreta"})
        self.assertContains(resposta, "Usuário ou senha inválidos.")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_conta_inativa_nao_autentica_nem_expoe_o_motivo(self):
        Usuario.objects.filter(pk=self.usuario.pk).update(is_active=False)
        resposta = self.client.post(self.entrar, {"username": "aluna", "password": SENHA_TESTE})
        self.assertContains(resposta, "Usuário ou senha inválidos.")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_inativacao_bloqueia_sessao_existente_na_proxima_requisicao(self):
        self.client.force_login(self.usuario)
        Usuario.objects.filter(pk=self.usuario.pk).update(is_active=False)
        self.assertRedirects(self.client.get("/"), self.entrar + "?next=/")

    def test_cookie_de_sessao_invalido_nao_libera_o_inicio(self):
        self.client.cookies["sessionid"] = "sessao-inexistente"
        self.assertRedirects(self.client.get("/"), self.entrar + "?next=/")

    def test_sessao_de_usuario_inexistente_nao_libera_o_inicio(self):
        self.client.force_login(self.usuario)
        sessao = self.client.session
        sessao["_auth_user_id"] = "999999"
        sessao.save()
        self.assertRedirects(self.client.get("/"), self.entrar + "?next=/")

    def test_next_externo_nao_redireciona_para_outro_site(self):
        resposta = self.client.post(self.entrar, {
            "username": "aluna", "password": SENHA_TESTE, "next": "https://fora.invalid/",
        })
        self.assertRedirects(resposta, reverse("inicio"))

    def test_next_local_e_preservado(self):
        resposta = self.client.post(self.entrar, {
            "username": "aluna", "password": SENHA_TESTE, "next": "/?origem=login",
        })
        self.assertRedirects(resposta, "/?origem=login")

    def test_logout_por_get_e_recusado_e_post_encerra_sessao(self):
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get(self.sair).status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)
        self.assertRedirects(self.client.post(self.sair), self.entrar)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertRedirects(self.client.get("/"), self.entrar + "?next=/")

    def test_csrf_e_exigido_no_login_e_logout(self):
        cliente = Client(enforce_csrf_checks=True)
        dados = {"username": "aluna", "password": SENHA_TESTE}
        self.assertEqual(cliente.post(self.entrar, dados).status_code, 403)
        cliente.get(self.entrar)
        token = cliente.cookies["csrftoken"].value
        self.assertEqual(cliente.post(self.entrar, {**dados, "csrfmiddlewaretoken": token}).status_code, 302)
        self.assertEqual(cliente.post(self.sair).status_code, 403)
        self.assertIn("_auth_user_id", cliente.session)
        token = cliente.cookies["csrftoken"].value
        self.assertEqual(cliente.post(self.sair, {"csrfmiddlewaretoken": token}).status_code, 302)
        self.assertNotIn("_auth_user_id", cliente.session)

    def test_nome_pessoal_e_escapado_no_html(self):
        Usuario.objects.filter(pk=self.usuario.pk).update(first_name="<script>alert(1)</script>")
        self.client.force_login(self.usuario)
        resposta = self.client.get("/")
        self.assertNotContains(resposta, "<script>")
        self.assertContains(resposta, "&lt;script&gt;")

    def test_nao_ha_cadastro_publico(self):
        self.assertEqual(self.client.get("/conta/cadastrar/").status_code, 404)
