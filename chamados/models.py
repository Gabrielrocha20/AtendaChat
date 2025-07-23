from django.db import models
from django.utils import timezone

from clientes.models import Cliente
from usuarios.models import CustomUser


class ClienteFinal(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='clientes_finais')
    nome = models.CharField(max_length=255)
    numero_whatsapp = models.CharField(max_length=20, unique=True)
    descricao = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.numero_whatsapp})"


class Chamado(models.Model):
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('em_atendimento', 'Em Atendimento'),
        ('resolvido', 'Resolvido'),
        ('fechado', 'Fechado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='chamados')
    cliente_final = models.ForeignKey(ClienteFinal, on_delete=models.CASCADE, related_name='chamados')
    usuario = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='chamados')
    assunto = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberto')
    criado_em = models.DateTimeField(default=timezone.now)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.cliente_final.nome} - {self.assunto} ({self.status})"


class Mensagem(models.Model):
    ORIGEM_CHOICES = [
        ('cliente', 'Cliente'),
        ('agente', 'Agente'),
    ]

    chamado = models.ForeignKey(Chamado, on_delete=models.CASCADE, related_name='mensagens')
    origem = models.CharField(max_length=10, choices=ORIGEM_CHOICES)
    texto = models.TextField()
    anexo = models.FileField(upload_to='anexos/', null=True, blank=True)
    data = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"[{self.origem}] {self.texto[:30]}"
