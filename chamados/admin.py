from django.contrib import admin

from .models import Chamado, ClienteFinal, Mensagem


@admin.register(ClienteFinal)
class ClienteFinalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'numero_whatsapp', 'cliente', 'criado_em')
    search_fields = ('nome', 'numero_whatsapp')
    list_filter = ('cliente',)


@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):
    list_display = ('cliente_final', 'assunto', 'status', 'cliente', 'usuario', 'criado_em')
    list_filter = ('status', 'cliente')
    search_fields = ('cliente_final__nome', 'assunto')
    autocomplete_fields = ['cliente_final', 'usuario']


@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    list_display = ('chamado', 'origem', 'texto_curto', 'data')
    list_filter = ('origem', 'data')
    search_fields = ('texto',)
    autocomplete_fields = ['chamado']

    def texto_curto(self, obj):
        return obj.texto[:50] + "..." if len(obj.texto) > 50 else obj.texto
    texto_curto.short_description = 'Texto'
