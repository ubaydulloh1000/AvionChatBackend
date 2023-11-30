from django.db.models import Case, When, BooleanField, Value
from rest_framework import generics, permissions, exceptions, filters
from django_filters.rest_framework import DjangoFilterBackend
from . import models, serializers


class ChatCreateView(generics.CreateAPIView):
    serializer_class = serializers.ChatCreateSerializer
    queryset = models.Chat.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class GroupCreateView(generics.CreateAPIView):
    serializer_class = serializers.GroupCreateSerializer
    queryset = models.Chat.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, type=models.Chat.ChatTypeChoices.GROUP.value)


class GroupOrChannelMemberCreateView(generics.CreateAPIView):
    serializer_class = serializers.GroupOrChannelMemberCreateSerializer
    model = models.ChatMembership
    permission_classes = [permissions.IsAuthenticated]


class ChannelCreateView(generics.CreateAPIView):
    serializer_class = serializers.ChannelCreateSerializer
    queryset = models.Chat.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, type=models.Chat.ChatTypeChoices.CHANNEL.value)


class ChatListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.ChatListSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ("is_archived",)
    search_fields = ("chat__name", 'chat__members__first_name', 'chat__members__last_name',)

    def get_queryset(self):
        qs = self.request.user.chat_memberships.all().select_related("chat")
        qs = qs.annotate_last_message(outer_ref_name="chat_id")
        qs = qs.annotate_unseen_messages_count(self.request.user)
        return qs.order_by("-updated_at", "-last_message_created_at")


class ChatDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.ChatDetailSerializer

    def get_object(self):
        user = self.request.user
        chat_membership = models.ChatMembership.objects.filter(
            chat_id=self.kwargs.get("chat_id"),
            user_id=user.id,
        ).first()

        if chat_membership is None:
            raise exceptions.NotFound()
        return chat_membership


class MessageListView(generics.ListAPIView):
    serializer_class = serializers.MessageListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ("content",)
    queryset = models.Message.objects.active()

    def get_queryset(self):
        chat = models.Chat.objects.filter(id=self.kwargs.get("pk")).first()
        if chat is None:
            return self.queryset.none()

        if not chat.is_permitted(self.request.user):
            raise exceptions.PermissionDenied()

        qs = self.queryset.filter(chat=chat).annotate(
            is_own_message=Case(
                When(sender_id=self.request.user.id, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        )
        return qs.order_by("-created_at")
