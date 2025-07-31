from django.urls import path

from .views import (ChamadoDetailView, ChamadoListCreateView,
                    ChamadoPartialUpdateView, ClienteFinalDetailView,
                    ClienteFinalListCreateView, MensagemDetailView,
                    MensagemListCreateView, ResponderChamadoView,
                    WebhookChamadoView)

urlpatterns = [
    # Chamados
    path('', ChamadoListCreateView.as_view(), name='chamado-list-create'),
    path('<int:pk>/', ChamadoDetailView.as_view(), name='chamado-detail'),
    path('webhook/', WebhookChamadoView.as_view(), name='chamado-webhook'),
    path('<int:pk>/responder/', ResponderChamadoView.as_view(), name='chamado-responder'),
    path('<int:pk>/atualizar/', ChamadoPartialUpdateView.as_view(), name='chamado-atualizar'),

    # Clientes Finais
    path('clientes-finais/', ClienteFinalListCreateView.as_view(), name='clientefinal-list-create'),
    path('clientes-finais/<int:pk>/', ClienteFinalDetailView.as_view(), name='clientefinal-detail'),

    # Mensagens
    path('mensagens/', MensagemListCreateView.as_view(), name='mensagem-list-create'),
    path('mensagens/<int:pk>/', MensagemDetailView.as_view(), name='mensagem-detail'),
]
