from django.db import models


class Cliente(models.Model):
    nome_fantasia = models.CharField(max_length=100)
    razao_social = models.CharField(max_length=150, blank=True)
    cnpj = models.CharField(max_length=18, blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    valor_mensalidade = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    data_contrato = models.DateField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    qtd_funcionarios = models.PositiveIntegerField(default=1)

    evolution_instance_id = models.CharField(max_length=100, blank=True, null=True)
    evolution_qrcode = models.TextField(blank=True, null=True)  # pode ser base64 do QR code

    def __str__(self):
        return self.nome_fantasia

    @property
    def usuarios_ativos(self):
        return self.usuarios.filter(is_active=True).count()