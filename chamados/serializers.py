from rest_framework import serializers

from .models import Chamado, ClienteFinal, Mensagem


class ClienteFinalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClienteFinal
        fields = '__all__'


class MensagemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensagem
        fields = '__all__'


class ChamadoSerializer(serializers.ModelSerializer):
    mensagens = MensagemSerializer(many=True, read_only=True)

    class Meta:
        model = Chamado
        fields = '__all__'
