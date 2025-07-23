from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    list_display = ('email', 'nome', 'cliente', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'cliente')
    search_fields = ('email', 'nome')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informações Pessoais'), {'fields': ('nome', 'cliente')}),
        (_('Permissões'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Permissões do Sistema'), {
            'fields': ('pode_ver_avaliacoes', 'pode_ver_relatorios'),
        }),
        (_('Datas Importantes'), {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'cliente', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
