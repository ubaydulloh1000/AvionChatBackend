from rest_framework import serializers

from apps.accounts import models


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
        )
        extra_kwargs = {
            "password": {
                "write_only": True,
            }
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user


class _AccountSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AccountSettings
        fields = (
            "show_last_seen",
            "show_read_receipts",
            "allow_to_add_groups",
            "allow_private_messages_to_non_contacts",
            "push_notifications_enabled",
        )


class AccountDetailSerializer(serializers.ModelSerializer):
    """
    This serializer class serializes the account detail of the currently logged-in user.
    """
    account_settings = _AccountSettingsSerializer()

    class Meta:
        model = models.User
        fields = (
            'id',
            "username",
            'email',
            'first_name',
            'last_name',
            "avatar",
            'date_joined',
            "account_settings",
        )
