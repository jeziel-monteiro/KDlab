from django.contrib.auth.forms import AuthenticationForm


class FormularioEntrada(AuthenticationForm):
    error_messages = {
        "invalid_login": "Usuário ou senha inválidos.",
        "inactive": "Usuário ou senha inválidos.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Nome de usuário"
        self.fields["username"].widget.attrs.update({
            "autocomplete": "username",
            "autocapitalize": "none",
            "spellcheck": "false",
            "placeholder": "Seu nome de usuário",
        })
        self.fields["password"].label = "Senha"
        self.fields["password"].widget.attrs.update({
            "autocomplete": "current-password",
            "placeholder": "Sua senha",
        })
