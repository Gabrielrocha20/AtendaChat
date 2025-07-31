import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

from .utils import enviar_mensagem_whatsapp


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chamado_id = self.scope['url_route']['kwargs']['chamado_id']
        self.room_group_name = f'chamado_{self.chamado_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        texto = data.get('texto')
        usuario_id = data.get('usuario_id')

        if not texto or not usuario_id:
            return  # você pode enviar uma resposta de erro se quiser

        from chamados.models import Chamado, Mensagem
        from usuarios.models import CustomUser

        try:
            chamado = await sync_to_async(Chamado.objects.select_related('cliente_final').get)(pk=self.chamado_id)
            usuario = await sync_to_async(CustomUser.objects.select_related('cliente').get)(pk=usuario_id)
        except (Chamado.DoesNotExist, CustomUser.DoesNotExist):
            return

        # Associa o usuário ao chamado se ainda não estiver definido
        if not chamado.usuario_id:
            chamado.usuario = usuario
            await sync_to_async(chamado.save)()

        # Formata o texto
        texto_formatado = f"*{usuario.nome}*: {texto}"

        # Salva a mensagem no banco
        mensagem = await sync_to_async(Mensagem.objects.create)(
            chamado=chamado,
            origem='agente',
            texto=texto_formatado,
            data=timezone.now()
        )

        # Envia para o grupo WebSocket (broadcast)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'mensagem': {
                    'texto': mensagem.texto,
                    'usuario': usuario.nome,
                    'data': mensagem.data.isoformat(),
                }
            }
        )

        # Envia a mensagem via Evolution API
        numero = chamado.cliente_final.numero_whatsapp
        nome_fantasia = usuario.cliente.nome_fantasia
        await sync_to_async(enviar_mensagem_whatsapp)(
            numero=numero,
            texto=texto_formatado,
            instancia=nome_fantasia
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['mensagem']))
