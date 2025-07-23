from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Cliente


class ClienteAPITestCase(APITestCase):

    def setUp(self):
        # Criar um cliente inicial para os testes
        self.cliente = Cliente.objects.create(
            nome_fantasia="Empresa Teste",
            razao_social="Empresa Teste LTDA",
            cnpj="12.345.678/0001-90",
            telefone="123456789",
            email="teste@empresa.com",
            valor_mensalidade=199.99,
            qtd_funcionarios=10
        )

    def test_listar_clientes(self):
        url = reverse('cliente-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    def test_criar_cliente_valido(self):
        url = reverse('cliente-create')
        data = {
            "nome_fantasia": "Nova Empresa",
            "razao_social": "Nova Empresa Ltda",
            "cnpj": "98.765.432/0001-11",
            "telefone": "987654321",
            "email": "contato@novaempresa.com",
            "valor_mensalidade": "299.90",
            "qtd_funcionarios": 25
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nome_fantasia'], data['nome_fantasia'])

    def test_criar_cliente_invalido(self):
        url = reverse('cliente-create')
        data = {
            "nome_fantasia": "",  # campo obrigatório vazio
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_detalhar_cliente_existente(self):
        url = reverse('cliente-detail', kwargs={'pk': self.cliente.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome_fantasia'], self.cliente.nome_fantasia)

    def test_detalhar_cliente_inexistente(self):
        url = reverse('cliente-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_atualizar_cliente_valido(self):
        url = reverse('cliente-update', kwargs={'pk': self.cliente.pk})
        data = {
            "nome_fantasia": "Empresa Atualizada",
            "razao_social": "Empresa Atualizada Ltda",
            "cnpj": "12.345.678/0001-90",
            "telefone": "111222333",
            "email": "atualizado@empresa.com",
            "valor_mensalidade": "150.00",
            "qtd_funcionarios": 15
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome_fantasia'], data['nome_fantasia'])

    def test_atualizar_cliente_invalido(self):
        url = reverse('cliente-update', kwargs={'pk': self.cliente.pk})
        data = {
            "nome_fantasia": "",  # inválido, vazio
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_deletar_cliente_existente(self):
        url = reverse('cliente-delete', kwargs={'pk': self.cliente.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Cliente.objects.filter(pk=self.cliente.pk).exists())

    def test_deletar_cliente_inexistente(self):
        url = reverse('cliente-delete', kwargs={'pk': 9999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
