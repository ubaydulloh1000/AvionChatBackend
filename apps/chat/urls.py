from django.urls import path

from . import views

urlpatterns = [
    path("chatCreate/", views.ChatCreateView.as_view(), name="chat-create"),
    path("chatList/", views.ChatListView.as_view(), name="chat-list"),
    path(
        "chatDetail/<int:chat_id>/",
        views.ChatDetailView.as_view(),
        name="chat-detail",
    ),
    path(
        "<int:pk>/messages/",
        views.MessageListView.as_view(),
        name="message-list",
    ),
]
