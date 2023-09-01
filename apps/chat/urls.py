from django.urls import path

from . import views

urlpatterns = [
    path("chatCreate/", views.ChatCreateView.as_view(), name="chat-create"),
    path("chatList/", views.ChatListView.as_view(), name="chat-list"),
]
