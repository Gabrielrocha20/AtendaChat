from django.urls import path

from .views import (CustomUserCreateView, CustomUserDeleteView,
                    CustomUserDetailView, CustomUserListView,
                    CustomUserUpdateView)

urlpatterns = [
    path('', CustomUserListView.as_view(), name='user-list'),
    path('create/', CustomUserCreateView.as_view(), name='user-create'),
    path('<int:pk>/', CustomUserDetailView.as_view(), name='user-detail'),
    path('<int:pk>/update/', CustomUserUpdateView.as_view(), name='user-update'),
    path('<int:pk>/delete/', CustomUserDeleteView.as_view(), name='user-delete'),
]
