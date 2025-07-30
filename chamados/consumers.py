import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

from .utils import enviar_mensagem_whatsapp  # ajuste o import


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

        from chamados.models import Chamado, Mensagem
        from usuarios.models import CustomUser

        try:
            chamado = await sync_to_async(Chamado.objects.get)(pk=self.chamado_id)
            usuario = await sync_to_async(CustomUser.objects.get)(pk=usuario_id)
        except Exception:
            return

        mensagem = await sync_to_async(Mensagem.objects.create)(
            chamado=chamado,
            origem='agente',
            texto=f"*{usuario.nome}*: {texto}",
            data=timezone.now()
        )

        # Enviar a mensagem para o grupo WebSocket (como antes)
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

        # Agora, chamar a função que envia via Evolution API para o WhatsApp
        # Use sync_to_async para chamar função síncrona em async
        @sync_to_async
        def get_numero():
            return chamado.cliente_final.numero_whatsapp
        @sync_to_async
        def get_nome_fantasia_do_cliente(usuario):
            # Essa função é síncrona, mas será chamada async-safe
            return usuario.cliente.nome_fantasia
        
        numero = await get_numero()
        nome_fantasia = await get_nome_fantasia_do_cliente(usuario)
        await sync_to_async(enviar_mensagem_whatsapp)(
            numero=numero,
            texto=mensagem.texto,
            instancia=nome_fantasia
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['mensagem']))
