from django.urls import path

from .views import (ChamadoDetailView, ChamadoListCreateView,
                    ClienteFinalDetailView, ClienteFinalListCreateView,
                    MensagemDetailView, MensagemListCreateView,
                    ResponderChamadoView, WebhookChamadoView)

urlpatterns = [
    # Chamados
    path('create/', ChamadoListCreateView.as_view(), name='chamado-list-create'),
    path('<int:pk>/', ChamadoDetailView.as_view(), name='chamado-detail'),
    path('webhook/', WebhookChamadoView.as_view(), name='chamado-webhook'),
    path('<int:pk>/responder/', ResponderChamadoView.as_view(), name='chamado-responder'),

    # Clientes Finais
    path('clientes-finais/', ClienteFinalListCreateView.as_view(), name='clientefinal-list-create'),
    path('clientes-finais/<int:pk>/', ClienteFinalDetailView.as_view(), name='clientefinal-detail'),

    # Mensagens
    path('mensagens/', MensagemListCreateView.as_view(), name='mensagem-list-create'),
    path('mensagens/<int:pk>/', MensagemDetailView.as_view(), name='mensagem-detail'),
]
