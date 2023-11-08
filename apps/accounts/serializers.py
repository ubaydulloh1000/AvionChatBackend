from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from apps.accounts import models
from .models import User, UserConfirmationCode
from .serializer_fields import PasswordField, UsernameField, EmailField
from apps.common.utils import generate_otp, send_otp_to_email


class UserRegisterSerializer(serializers.ModelSerializer):
    username = UsernameField(write_only=True)
    email = EmailField(write_only=True)
    password = PasswordField()
    token = serializers.CharField(read_only=True)

    class Meta:
        model = models.User
        fields = (
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "token",
        )
        extra_kwargs = {
            "first_name": {"required": True, "write_only": True},
            "last_name": {"required": True, "write_only": True},
            "email": {"required": True, "write_only": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user_code = UserConfirmationCode(
            user=instance,
            code_type=UserConfirmationCode.CodeTypeChoices.REGISTER.value,
            code=generate_otp(),
            expire_at=timezone.now() + timedelta(minutes=2),
        )
        user_code.save()

        send_otp_to_email(
            otp=user_code.code,
            receivers=[instance.email],
        )
        data["token"] = user_code.token
        return data


class UserRegisterConfirmSerializer(serializers.ModelSerializer):
    token = serializers.CharField(
        write_only=True,
        error_messages={
            "blank": "Token can not be blank.",
            "required": "Token is required.",
        }
    )
    otp = serializers.CharField(
        write_only=True,
        min_length=4,
        max_length=4,
        error_messages={
            "blank": "OTP can not be blank.",
            "required": "OTP is required.",
            "min_length": "OTP must be 4 chars.",
            "max_length": "OTP must be 4 chars.",
        }
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "token",
            "otp",
        )
        extra_kwargs = {
            "username": {"read_only": True},
        }

    def create(self, validated_data):
        return User.objects.first()


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


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "avatar",
            "is_online",
            "last_seen_at",
        )


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "avatar",
            "is_online",
            "last_seen_at",
        )
