from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from clientes.models import Cliente
from usuarios.models import CustomUser


class CustomUserAPITestCase(APITestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(nome='Cliente Teste')
        self.user = CustomUser.objects.create_user(
            email='user@test.com',
            nome='Usuário Teste',
            cliente=self.cliente,
            password='senha123'
        )
        self.superuser = CustomUser.objects.create_superuser(
            email='admin@test.com',
            nome='Admin',
            cliente=self.cliente,
            password='admin123'
        )
        self.create_url = reverse('user-create')
        self.list_url = reverse('user-list')

    def test_create_user(self):
        data = {
            'email': 'novo@test.com',
            'nome': 'Novo Usuário',
            'cliente': self.cliente.id,
            'password': 'novaSenha123',
            'is_active': True
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], data['email'])

    def test_list_users(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_user_detail(self):
        url = reverse('user-detail', kwargs={'pk': self.user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_update_user(self):
        url = reverse('user-update', kwargs={'pk': self.user.pk})
        data = {
            'email': 'user_updated@test.com',
            'nome': 'Usuário Atualizado',
            'cliente': self.cliente.id,
            'password': 'novaSenha456',
            'is_active': True
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], data['email'])

    def test_delete_user(self):
        url = reverse('user-delete', kwargs={'pk': self.user.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomUser.objects.filter(pk=self.user.pk).exists())
