from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models

from clientes.models import Cliente


class UsuarioManager(BaseUserManager):
    def create_user(self, email, nome, cliente, password=None, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório')
        if not cliente:
            raise ValueError('O cliente é obrigatório')
        
        email = self.normalize_email(email)
        user = self.model(email=email, nome=nome, cliente=cliente, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, cliente, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, nome, cliente, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='usuarios', null=True, blank=True, default=None)
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Permissões específicas
    pode_ver_avaliacoes = models.BooleanField(default=False)
    pode_ver_relatorios = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'cliente']

    def __str__(self):
        return f'{self.nome} ({self.email})'
