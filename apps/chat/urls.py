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
        "groupCreate/",
        views.GroupCreateView.as_view(),
        name="group-create",
    ),
    path(
        "groupOrChannelMemberCreate/",
        views.GroupOrChannelMemberCreateView.as_view(),
        name="group-or-channel-member-create",
    ),
    path(
        "channelCreate/",
        views.ChannelCreateView.as_view(),
        name="channel-create",
    ),
    path(
        "<int:pk>/messages/",
        views.MessageListView.as_view(),
        name="message-list",
    ),
    path(
        "chatMembershipUpdate/<int:pk>/",
        views.ChatMembershipUpdateAPIView.as_view(),
        name="chatMembershipUpdate"
    ),
]
