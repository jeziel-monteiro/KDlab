from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    """Contas locais; perfis e vínculos do domínio serão acrescentados depois."""

    class Meta(AbstractUser.Meta):
        abstract = False
        verbose_name = "usuário"
        verbose_name_plural = "usuários"
