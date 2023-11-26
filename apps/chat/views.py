from django.db.models import Case, When, BooleanField, Value
from rest_framework import generics, permissions, exceptions, filters
from django_filters.rest_framework import DjangoFilterBackend
from . import models, serializers


class ChatCreateView(generics.CreateAPIView):
    serializer_class = serializers.ChatCreateSerializer
    queryset = models.Chat.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class ChatListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.ChatListSerializer
    # queryset = models.ChatMembership.objects.all()

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ("is_archived",)

    def get_queryset(self):
        qs = self.request.user.chat_memberships.all()
        qs = qs.annotate_last_message(outer_ref_name="chat_id")
        qs = qs.annotate_unseen_messages_count(self.request.user)
        return qs.order_by("-last_message_created_at")
        # return qs.order_by("-chat__messages__created_at").distinct()

    # def filter_queryset(self, queryset):
    #     search_query = self.request.query_params.get("search", None)
    #     user = self.request.user
    #     # queryset =
    #
    #     # group_chats = user.group_memberships.annotate_unseen_messages_count(user) \
    #     #     .annotate_last_message(outer_ref_name="group_id")
    #     # channel_chats = user.channel_subscriptions.annotate_unseen_messages_count(user). \
    #     #     annotate_last_message(outer_ref_name="channel_id")
    #     # private_chats = user.private_chat_memberships.annotate_unseen_messages_count(user). \
    #     #     annotate_last_message(outer_ref_name="chat_id")
    #
    #     # is_archived = self.request.query_params.get("is_archived", None)
    #     # if is_archived is not None:
    #     #     is_archived = is_archived.lower() == "true"
    #     #
    #     #     group_chats = group_chats.filter(is_archived=is_archived)
    #     #     channel_chats = channel_chats.filter(is_archived=is_archived)
    #     #     private_chats = private_chats.filter(is_archived=is_archived)
    #     #
    #     # if search_query:
    #     #     search_query = search_query.lower()
    #     #     group_chats = group_chats.filter(group__name__icontains=search_query)
    #     #     channel_chats = channel_chats.filter(channel__name__icontains=search_query)
    #     #     private_chats = private_chats.search_by_interlocutor(search_query, user)
    #     #
    #     # group_chats.order_by("-group__messages__created_at")
    #     # channel_chats.order_by("-channel__messages__created_at")
    #     # private_chats.order_by("-chat__messages__created_at")
    #
    #     # return private_chats
    #     return queryset.filter(user=user).order_by("-updated_at")


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
    filter_backends = (DjangoFilterBackend,)
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
