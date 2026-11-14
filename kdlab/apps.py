from django.contrib.admin.apps import AdminConfig


class AdministracaoConfig(AdminConfig):
    default_site = "kdlab.admin.AdministracaoSite"
