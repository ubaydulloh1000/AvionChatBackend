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

    def validate(self, attrs):
        match attrs['type']:
            case models.Chat.ChatTypeChoices.PRIVATE:
                if attrs.get("user") is not None and models.Chat.objects.filter(
                        user1=self.context["request"].user, user2=attrs["user"]
                ).exists():
                    raise serializers.ValidationError(
                        code="already_exists_chat", detail={"user": "Private chat between these users already exists."}
                    )
        return attrs

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        chat_type = validated_data['type']

        if chat_type == models.Chat.ChatTypeChoices.PRIVATE:
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
            chat_membership_1 = models.PrivateChatMembership(
                chat=chat, user=chat.user1
            )
            chat_membership_2 = models.PrivateChatMembership(
                chat=chat, user=chat.user2
            )
            chat_membership_1.save()
            chat_membership_2.save()
        return chat


class ChatListSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Chat
        fields = (
            'id',
            # 'chat',
            "is_archived",
            "is_muted",
            'created_at',
            'updated_at',
        )
