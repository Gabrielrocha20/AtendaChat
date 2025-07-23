from django.urls import path

from .views import (ClienteCreateView, ClienteDeleteView, ClienteDetailView,
                    ClienteListView, ClienteUpdateView)

urlpatterns = [
    path('', ClienteListView.as_view(), name='cliente-list'),
    path('create/', ClienteCreateView.as_view(), name='cliente-create'),
    path('<int:pk>/', ClienteDetailView.as_view(), name='cliente-detail'),
    path('<int:pk>/update/', ClienteUpdateView.as_view(), name='cliente-update'),
    path('<int:pk>/delete/', ClienteDeleteView.as_view(), name='cliente-delete'),
]
