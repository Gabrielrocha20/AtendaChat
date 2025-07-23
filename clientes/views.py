import requests
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cliente
from .serializers import ClienteSerializer
from .utils import criar_instancia_evolution, salvar_qrcode_base64


class ClienteCreateView(APIView):
    def post(self, request):
        serializer = ClienteSerializer(data=request.data)
        if serializer.is_valid():
            cliente = serializer.save()

            try:
                data = criar_instancia_evolution(instance_name=cliente.nome_fantasia)
                cliente.evolution_instance_id = data.get("instance")["instanceId"]  # corrigido!
                base64_qrcode = data.get("qrcode")["base64"]
                if base64_qrcode:
                    path = salvar_qrcode_base64(base64_qrcode, cliente.nome_fantasia.replace(" ", "_").lower())
                    cliente.evolution_qrcode = path
                cliente.save()
            except requests.RequestException as e:
                cliente.delete()
                return Response(
                    {"error": "Erro ao criar instância na Evolution."},
                    status=status.HTTP_502_BAD_GATEWAY
                )

            # Recria o serializer com o cliente atualizado
            serializer = ClienteSerializer(cliente)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClienteListView(APIView):
    def get(self, request):
        clientes = Cliente.objects.all()
        serializer = ClienteSerializer(clientes, many=True)
        return Response(serializer.data)


class ClienteDetailView(APIView):
    def get_object(self, pk):
        try:
            return Cliente.objects.get(pk=pk)
        except Cliente.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        cliente = self.get_object(pk)
        serializer = ClienteSerializer(cliente)
        return Response(serializer.data)

class ClienteUpdateView(APIView):
    def get_object(self, pk):
        try:
            return Cliente.objects.get(pk=pk)
        except Cliente.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        cliente = self.get_object(pk)
        serializer = ClienteSerializer(cliente, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClienteDeleteView(APIView):
    def get_object(self, pk):
        try:
            return Cliente.objects.get(pk=pk)
        except Cliente.DoesNotExist:
            raise Http404

    def delete(self, request, pk):
        cliente = self.get_object(pk)
        cliente.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
