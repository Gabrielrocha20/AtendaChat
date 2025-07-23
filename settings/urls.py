from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
# drf_yasg
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="AtendaChat API",
      default_version='v1',
      description="Documentação da API do sistema de chamados via WhatsApp",
      terms_of_service="https://www.seusite.com/termos",
      contact=openapi.Contact(email="suporte@seudominio.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/clientes/', include('clientes.urls')),
    path('api/usuarios/', include('usuarios.urls')),
    path('api/chamados/', include('chamados.urls')),

    # Swagger e Redoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
