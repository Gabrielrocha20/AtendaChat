from django.conf import settings
from rest_framework import serializers

from .models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    evolution_qrcode_url = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = '__all__'  # ou liste os campos explicitamente
        read_only_fields = ['evolution_qrcode_url']

    def get_evolution_qrcode_url(self, obj):
        if obj.evolution_qrcode:
            return f"{settings.MEDIA_URL}{obj.evolution_qrcode}"
        return None
