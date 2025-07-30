import base64
import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from chamados.models import Chamado, Cliente, ClienteFinal, Mensagem
from clientes.models import Cliente
from usuarios.models import CustomUser

from .models import Chamado, ClienteFinal, Mensagem
from .serializers import (ChamadoSerializer, ClienteFinalSerializer,
                          MensagemSerializer)
from .utils import enviar_mensagem_whatsapp

# --- Chamado Views ---

class ChamadoListCreateView(APIView):
    def get(self, request):
        chamados = Chamado.objects.all().order_by('-criado_em')
        serializer = ChamadoSerializer(chamados, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ChamadoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ChamadoStatusUpdateView(APIView):
    def patch(self, request, pk):
        chamado = get_object_or_404(Chamado, pk=pk)
        novo_status = request.data.get('status')

        if novo_status not in dict(Chamado.STATUS_CHOICES):
            return Response({'error': 'Status inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        chamado.status = novo_status
        chamado.save()

        serializer = ChamadoSerializer(chamado)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChamadoDetailView(APIView):
    def get_object(self, pk):
        try:
            return Chamado.objects.get(pk=pk)
        except Chamado.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        chamado = self.get_object(pk)
        serializer = ChamadoSerializer(chamado)
        return Response(serializer.data)

    def put(self, request, pk):
        chamado = self.get_object(pk)
        serializer = ChamadoSerializer(chamado, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        chamado = self.get_object(pk)
        chamado.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- Webhook (recebe mensagens da Evolution API) ---

class WebhookChamadoView(APIView):
    permission_classes = []  # Webhook público (adicionar autenticação se necessário)

    def post(self, request):
        data = request.data

        instance_name = data.get("instance")
        sender = data.get("sender")  # ex: '5524988236757@s.whatsapp.net'
        message_data = data.get("data", {})
        nome = message_data.get("pushName", "Cliente")

        numero = sender.split("@")[0]

        # Busca o cliente
        try:
            cliente = Cliente.objects.get(nome_fantasia=instance_name)
        except Cliente.DoesNotExist:
            return Response({"error": "Cliente não encontrado."}, status=400)

        cliente_final, _ = ClienteFinal.objects.get_or_create(
            numero_whatsapp=numero,
            defaults={"nome": nome, "cliente": cliente}
        )

        # Verifica se há chamado em andamento
        chamado = Chamado.objects.filter(
            cliente_final=cliente_final,
            status__in=["aberto", "em_atendimento"]
        ).first()

        if not chamado:
            chamado = Chamado.objects.create(
                cliente=cliente,
                cliente_final=cliente_final,
                assunto=f"Novo atendimento de {nome}",
                status="aberto"
            )

        texto = None
        anexo = None

        message = message_data.get("message", {})
        message_type = message_data.get("messageType")

        if message_type == "conversation":
            texto = message.get("conversation")

        elif "audioMessage" in message:
            # Exemplo: o Evolution pode enviar base64 ou URL; aqui tratamos base64
            base64_audio = message["audioMessage"].get("base64")
            if base64_audio:
                anexo = self.salvar_arquivo_base64(base64_audio, numero, "audio", "ogg")
                texto = "[Áudio recebido]"

        elif "imageMessage" in message:
            base64_img = message["imageMessage"].get("base64")
            if base64_img:
                anexo = self.salvar_arquivo_base64(base64_img, numero, "imagem", "jpg")
                texto = "[Imagem recebida]"

        if texto:
            Mensagem.objects.create(
                chamado=chamado,
                origem="cliente",
                texto=texto,
                anexo=anexo,
                data=timezone.now()
            )

        return Response({"success": True}, status=status.HTTP_201_CREATED)

    def salvar_arquivo_base64(self, base64_data, numero, tipo, ext):
        """
        Salva o arquivo base64 na pasta media/anexos/<numero>/
        """
        diretorio = os.path.join(settings.MEDIA_ROOT, "anexos", numero)
        os.makedirs(diretorio, exist_ok=True)

        nome_arquivo = f"{tipo}_{timezone.now().strftime('%Y%m%d%H%M%S')}.{ext}"
        caminho_completo = os.path.join(diretorio, nome_arquivo)

        with open(caminho_completo, "wb") as f:
            f.write(base64.b64decode(base64_data))

        # Retorna o path relativo para ser salvo no campo FileField/ImageField se quiser
        return f"anexos/{numero}/{nome_arquivo}"


# --- Responder ao chamado (enviar mensagem via Evolution API) ---

class ResponderChamadoView(APIView):
    def post(self, request, pk):
        texto = request.data.get('texto')
        usuario_id = request.data.get('usuario')

        if not texto:
            return Response({'error': 'Texto é obrigatório'}, status=400)
        if not usuario_id:
            return Response({'error': 'Usuário é obrigatório'}, status=400)

        # Busca o usuário
        try:
            usuario = CustomUser.objects.get(pk=usuario_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Usuário não encontrado'}, status=404)
        print(usuario)
        # Pega o cliente associado ao usuário
        cliente = usuario.cliente
        if not cliente or not cliente.evolution_instance_id:
            return Response({'error': 'Cliente ou instância Evolution não encontrada para este usuário'}, status=400)

        # Busca o chamado
        try:
            chamado = Chamado.objects.get(pk=pk)
        except Chamado.DoesNotExist:
            return Response({'error': 'Chamado não encontrado'}, status=404)
        print(chamado)
        # Associa o usuário e a instância ao chamado, se ainda não definidos
        if not chamado.usuario:
            chamado.usuario = usuario
            chamado.save()

        # Formata o texto com o nome do usuário
        texto_formatado = f"*{usuario.nome}*: {texto}"

        Mensagem.objects.create(
            chamado=chamado,
            origem='agente',
            texto=texto_formatado,
            data=timezone.now()
        )
        print(cliente.evolution_instance_id)
        # Envia a mensagem via Evolution API
        status_code, resposta = enviar_mensagem_whatsapp(
            numero=chamado.cliente_final.numero_whatsapp,
            texto=texto_formatado,
            instancia=cliente.nome_fantasia
        )

        return Response({
            'status_code': status_code,
            'evolution_response': resposta
        }, status=status.HTTP_200_OK)

# --- ClienteFinal Views ---

class ClienteFinalListCreateView(APIView):
    def get(self, request):
        clientes = ClienteFinal.objects.all()
        serializer = ClienteFinalSerializer(clientes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClienteFinalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClienteFinalDetailView(APIView):
    def get_object(self, pk):
        try:
            return ClienteFinal.objects.get(pk=pk)
        except ClienteFinal.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        cliente = self.get_object(pk)
        serializer = ClienteFinalSerializer(cliente)
        return Response(serializer.data)

    def put(self, request, pk):
        cliente = self.get_object(pk)
        serializer = ClienteFinalSerializer(cliente, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        cliente = self.get_object(pk)
        cliente.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- Mensagem Views ---

class MensagemListCreateView(APIView):
    def get(self, request):
        mensagens = Mensagem.objects.all().order_by('data')
        serializer = MensagemSerializer(mensagens, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MensagemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MensagemDetailView(APIView):
    def get_object(self, pk):
        try:
            return Mensagem.objects.get(pk=pk)
        except Mensagem.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        mensagem = self.get_object(pk)
        serializer = MensagemSerializer(mensagem)
        return Response(serializer.data)

    def put(self, request, pk):
        mensagem = self.get_object(pk)
        serializer = MensagemSerializer(mensagem, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        mensagem = self.get_object(pk)
        mensagem.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
