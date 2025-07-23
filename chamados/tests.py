from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from clientes.models import Cliente
from usuarios.models import CustomUser

from .models import Chamado, ClienteFinal, Mensagem


class ChamadosTestCase(TestCase):
    def setUp(self):
        # Cliente (empresa)
        self.cliente = Cliente.objects.create(
            nome_fantasia="Empresa Teste",
            razao_social="Empresa Teste LTDA",
            cnpj="12.345.678/0001-90",
            telefone="123456789",
            email="teste@empresa.com",
            valor_mensalidade=199.99,
            qtd_funcionarios=10
        )

        # Usuário (agente)
        self.usuario = CustomUser.objects.create_user(
            email="agente@empresa.com",
            nome="Agente",
            cliente=self.cliente,
            password="senha123"
        )

        # Cliente final (usuário WhatsApp)
        self.cliente_final = ClienteFinal.objects.create(
            cliente=self.cliente,
            nome="João da Silva",
            numero_whatsapp="5511999999999",
            descricao="Cliente importante"
        )

        # Chamado
        self.chamado = Chamado.objects.create(
            cliente=self.cliente,
            cliente_final=self.cliente_final,
            usuario=self.usuario,
            assunto="Problema com o sistema",
            status="aberto"
        )

        # Mensagem
        self.mensagem = Mensagem.objects.create(
            chamado=self.chamado,
            origem="cliente",
            texto="Não estou conseguindo acessar minha conta.",
            data=timezone.now()
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.usuario)

    # ---------- TESTES DOS MODELOS ----------
    def test_model_cliente_final(self):
        self.assertEqual(self.cliente_final.nome, "João da Silva")
        self.assertEqual(self.cliente_final.numero_whatsapp, "5511999999999")

    def test_model_chamado(self):
        self.assertEqual(self.chamado.assunto, "Problema com o sistema")
        self.assertEqual(self.chamado.status, "aberto")

    def test_model_mensagem(self):
        self.assertEqual(self.mensagem.origem, "cliente")
        self.assertIn("acessar", self.mensagem.texto)

    # ---------- TESTES DAS VIEWS (API) ----------
    def test_create_cliente_final_api(self):
        url = reverse('clientefinal-list')
        data = {
            "cliente": self.cliente.id,
            "nome": "Maria Souza",
            "numero_whatsapp": "5511988888888",
            "descricao": "Nova cliente"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_chamados_api(self):
        url = reverse('chamado-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_update_chamado_api(self):
        url = reverse('chamado-detail', args=[self.chamado.id])
        data = {
            "cliente": self.cliente.id,
            "cliente_final": self.cliente_final.id,
            "usuario": self.usuario.id,
            "assunto": "Erro ao logar",
            "status": "em_atendimento"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.chamado.refresh_from_db()
        self.assertEqual(self.chamado.status, "em_atendimento")

    def test_delete_mensagem_api(self):
        url = reverse('mensagem-detail', args=[self.mensagem.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Mensagem.objects.filter(id=self.mensagem.id).exists())
