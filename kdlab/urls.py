from django.contrib import admin
from django.urls import include, path

from apps.identidade.views import inicio


admin.site.site_header = "KDlab · Administração"
admin.site.site_title = "Administração do KDlab"
admin.site.index_title = "Gestão de acesso"

urlpatterns = [
    path("", inicio, name="inicio"),
    path("conta/", include("apps.identidade.urls")),
    path("admin/", admin.site.urls),
]
