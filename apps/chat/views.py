from rest_framework import generics, permissions, exceptions
from django_filters.rest_framework import DjangoFilterBackend
from . import models, serializers


class ChatCreateView(generics.CreateAPIView):
    serializer_class = serializers.ChatCreateSerializer
    queryset = models.Chat.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class ChatListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.ChatListSerializer
    queryset = models.PrivateChatMembership.objects.all()

    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("is_archived",)

    def filter_queryset(self, queryset):
        user = self.request.user
        group_chats = user.group_memberships.all()
        channel_chats = user.channel_subscriptions.all()
        private_chats = user.private_chat_memberships.all()

        is_archived = self.request.query_params.get("is_archived", None)
        if is_archived is not None:
            is_archived = is_archived.lower() == "true"

            group_chats = group_chats.filter(is_archived=is_archived)
            channel_chats = channel_chats.filter(is_archived=is_archived)
            private_chats = private_chats.filter(is_archived=is_archived)
        return group_chats.union(channel_chats, private_chats)


class ChatDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.ChatDetailSerializer

    def get_object(self):
        user = self.request.user
        group_chats = user.group_memberships.filter(group_id=self.kwargs["chat_id"])
        channel_chats = user.channel_subscriptions.filter(channel_id=self.kwargs["chat_id"])
        private_chats = user.private_chat_memberships.filter(chat_id=self.kwargs["chat_id"])

        if group_chats.exists():
            return group_chats.first()
        elif channel_chats.exists():
            return channel_chats.first()
        elif private_chats.exists():
            return private_chats.first()
        else:
            raise exceptions.NotFound()


class MessageListView(generics.ListAPIView):
    serializer_class = serializers.MessageListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    queryset = models.Message.objects.all()

    def get_queryset(self):
        chat = models.Chat.objects.filter(id=self.kwargs["pk"]).first()
        if chat is None:
            raise exceptions.NotFound()

        if not chat.is_permitted(self.request.user):
            raise exceptions.PermissionDenied()

        qs = self.queryset.filter(chat=chat).order_by("-created_at")
        return qs
