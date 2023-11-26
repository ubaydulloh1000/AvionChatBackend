from django.db.models import Q
from rest_framework import serializers

from apps.accounts.models import User
from . import models


class ChatCreateSerializer(serializers.ModelSerializer):
    # user is only required for private chats
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, write_only=True
    )

    class Meta:
        model = models.Chat
        fields = (
            'id',
            'type',
            'name',
            'owner',
            "user",
            'created_at',
        )
        extra_kwargs = {
            "type": {"required": True},
            'owner': {'read_only': True},
            "name": {"required": False},
            'created_at': {'read_only': True},
        }

    @staticmethod
    def validate_type(chat_type):
        if chat_type != models.Chat.ChatTypeChoices.PRIVATE:
            raise serializers.ValidationError(
                "Only private chats are supported at the moment."
            )
        return chat_type

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        chat_type = validated_data['type']

        if chat_type == models.Chat.ChatTypeChoices.PRIVATE:
            old_chat = models.Chat.objects.filter(
                Q(user1=self.context["request"].user, user2=validated_data["user"]) |
                Q(user1=validated_data["user"], user2=self.context["request"].user)
            ).first()
            if old_chat is not None:
                return old_chat

            user = validated_data.get("user")
            if user is None:
                raise serializers.ValidationError(
                    code="required", detail={"user": "user is required for private chats"}
                )
            if user == validated_data["owner"]:
                raise serializers.ValidationError(
                    code="invalid", detail={"user": "user cannot be the owner"}
                )
            validated_data['name'] = f"{validated_data['owner'].username} and {validated_data['user'].username}"
            validated_data["user1"] = validated_data["owner"]
            validated_data["user2"] = validated_data.pop("user")

        elif chat_type == models.Chat.ChatTypeChoices.GROUP.value:
            # TODO: add group chat logic
            pass

        elif chat_type == models.Chat.ChatTypeChoices.CHANNEL.value:
            # TODO: add channel chat logic
            pass

        chat = super().create(validated_data)

        if chat_type == models.Chat.ChatTypeChoices.PRIVATE:
            chat.members.add(chat.user1, chat.user2)
            chat_membership_1 = models.ChatMembership(
                chat=chat, user=chat.user1
            )
            chat_membership_2 = models.ChatMembership(
                chat=chat, user=chat.user2
            )
            chat_membership_1.save()
            chat_membership_2.save()
        return chat


class ChatListSerializer(serializers.ModelSerializer):
    class _ChatSerializer(serializers.ModelSerializer):
        class _UserSerializer(serializers.ModelSerializer):
            full_name = serializers.CharField(source="get_full_name")

            class Meta:
                model = User
                fields = (
                    'id',
                    'username',
                    "full_name",
                    'avatar',
                )

        user = serializers.SerializerMethodField()

        class Meta:
            model = models.Chat
            fields = (
                "id",
                "name",
                "image",
                "type",
                "user",
            )

        def get_user(self, obj):
            if obj.type == models.Chat.ChatTypeChoices.PRIVATE:
                if obj.user1_id == self.context["request"].user.id:
                    return self._UserSerializer(obj.user2, context={"request": self.context["request"]}).data
                return self._UserSerializer(obj.user1, context={"request": self.context["request"]}).data
            return None

    chat = serializers.SerializerMethodField()
    unseen_messages_count = serializers.IntegerField(default=0)
    last_message_created_at = serializers.DateTimeField(read_only=True, default=None)
    last_message_content = serializers.CharField(read_only=True, default="")
    last_message_sender_id = serializers.IntegerField(read_only=True, default=None)
    last_message_is_seen = serializers.BooleanField(read_only=True, default=True)

    class Meta:
        model = models.PrivateChatMembership
        fields = (
            'id',
            "chat",
            "is_archived",
            "is_muted",
            "unseen_messages_count",
            "last_message_created_at",
            "last_message_content",
            "last_message_sender_id",
            "last_message_is_seen",
            'created_at',
            'updated_at',
        )

    def get_chat(self, obj):
        if hasattr(obj, "chat"):
            return self._ChatSerializer(obj.chat, context={"request": self.context["request"]}).data
        elif hasattr(obj, "group"):
            return self._ChatSerializer(obj.group, context={"request": self.context["request"]}).data
        elif hasattr(obj, "channel"):
            return self._ChatSerializer(obj.channel, context={"request": self.context["request"]}).data
        return None


class ChatDetailSerializer(serializers.ModelSerializer):
    class ChatSerializer(serializers.ModelSerializer):
        user = serializers.SerializerMethodField()

        class UserSerializer(serializers.ModelSerializer):
            class Meta:
                model = User
                fields = (
                    'id',
                    'username',
                    'avatar',
                    'first_name',
                    'last_name',
                    "last_seen_at",
                )

        class Meta:
            model = models.Chat
            fields = (
                "id",
                "name",
                "image",
                "type",
                "user",
            )

        def get_user(self, obj):
            if obj.type == models.Chat.ChatTypeChoices.PRIVATE:
                if obj.user1_id == self.context["request"].user.id:
                    return self.UserSerializer(obj.user2, context={"request": self.context["request"]}).data
                return self.UserSerializer(obj.user1, context={"request": self.context["request"]}).data
            return None

    chat = serializers.SerializerMethodField()

    class Meta:
        model = models.PrivateChatMembership
        fields = (
            'id',
            "chat",
            "is_archived",
            "is_muted",
            'created_at',
            'updated_at',
        )

    def get_chat(self, obj):
        if hasattr(obj, "chat"):
            return self.ChatSerializer(obj.chat, context={"request": self.context["request"]}).data
        elif hasattr(obj, "group"):
            return self.ChatSerializer(obj.group, context={"request": self.context["request"]}).data
        elif hasattr(obj, "channel"):
            return self.ChatSerializer(obj.channel, context={"request": self.context["request"]}).data
        return None


class MessageListSerializer(serializers.ModelSerializer):
    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = (
                'id',
                'username',
                'avatar',
                'first_name',
                'last_name',
                "last_seen_at",
            )

    sender = UserSerializer()
    recipient = UserSerializer()
    is_own_message = serializers.BooleanField(default=False)

    class Meta:
        model = models.Message
        fields = (
            "id",
            "chat",
            "type",
            "sender",
            "recipient",
            "content",
            "is_seen",
            "seen_at",
            "is_edited",
            "is_reacted",
            "created_at",
            "is_own_message",
        )


class MessageDetailSerializer(MessageListSerializer):
    is_own_message = serializers.SerializerMethodField()

    def get_is_own_message(self, obj):
        return obj.sender_id == self.context["user"].id
