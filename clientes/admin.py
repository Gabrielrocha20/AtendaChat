from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('email', 'cnpj', 'telefone', 'qtd_funcionarios', 'valor_mensalidade', 'ativo')
    search_fields = ('email', 'cnpj')
    list_filter = ('ativo',)
    ordering = ('nome_fantasia',)
