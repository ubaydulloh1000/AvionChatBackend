from rest_framework import generics, permissions
from . import models, serializers


class ChatCreateView(generics.CreateAPIView):
    serializer_class = serializers.ChatCreateSerializer
    queryset = models.Chat.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class ChatListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.ChatListSerializer

    def get_queryset(self):
        user = self.request.user
        group_chats = user.group_memberships.all()
        channel_chats = user.channel_subscriptions.all()
        private_chats = user.private_chat_memberships.all()

        return group_chats.union(channel_chats, private_chats)
