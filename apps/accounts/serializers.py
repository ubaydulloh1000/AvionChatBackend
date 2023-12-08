from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from apps.accounts import models
from .models import User, UserConfirmationCode
from .serializer_fields import PasswordField, UsernameField, EmailField
from apps.common import utils, tasks as common_tasks


class UserRegisterSerializer(serializers.ModelSerializer):
    email = EmailField(write_only=True)
    password = PasswordField()
    token = serializers.CharField(read_only=True)

    class Meta:
        model = models.User
        fields = (
            "email",
            "password",
            "token",
        )
        extra_kwargs = {
            "email": {"required": True, "write_only": True},
        }

    def create(self, validated_data):
        email = validated_data.get("email")
        password = validated_data.pop("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            validated_data["is_active"] = False
            user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.confirmation_codes.filter(expire_at__gte=timezone.now()).exists():
            user_code = instance.confirmation_codes.filter(expire_at__gte=timezone.now()).first()
        else:
            user_code = UserConfirmationCode(
                user=instance,
                code_type=UserConfirmationCode.CodeTypeChoices.REGISTER.value,
                code=utils.generate_otp(),
                expire_at=timezone.now() + timedelta(minutes=2),
            )
            user_code.save()

        common_tasks.send_mail_task.apply_async(
            [user_code.code, [instance.email]],
            countdown=1,
            queue="lightweight-tasks"
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
            "email",
            "token",
            "otp",
        )
        extra_kwargs = {
            "username": {"read_only": True},
            "email": {"read_only": True},
        }

    def validate(self, attrs):
        token = attrs["token"]
        otp = attrs["otp"]

        try:
            c_code = UserConfirmationCode.objects.get(token=token)
        except UserConfirmationCode.DoesNotExist:
            raise serializers.ValidationError(
                code="not_found",
                detail={"token": "Invalid Token!"}
            )

        if c_code.is_expired:
            raise serializers.ValidationError(
                code="expired",
                detail={"token": "Token expired!"}
            )

        if c_code.attempts >= 3:
            raise serializers.ValidationError(
                code="attempts",
                detail={"otp": "Too many wrong attempts!"}
            )

        if c_code.code != otp:
            c_code.attempts += 1
            c_code.save(update_fields=["attempts"])
            raise serializers.ValidationError(
                code="wrong",
                detail={"otp": "Wrong otp!"}
            )
        return attrs

    def create(self, validated_data):
        token = validated_data.pop("token")

        try:
            c_code = UserConfirmationCode.objects.get(token=token)
        except UserConfirmationCode.DoesNotExist:
            raise serializers.ValidationError(
                code="not_found",
                detail={"token": "Invalid Token!"}
            )
        c_code.user.is_active = True
        c_code.user.save(update_fields=["is_active"])

        c_code.expire_at = timezone.now()
        c_code.save(update_fields=["expire_at"])
        return c_code.user


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


class AccountDetailUpdateSerializer(serializers.ModelSerializer):
    account_settings = _AccountSettingsSerializer(read_only=True)

    class Meta:
        model = models.User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "avatar",
            "date_joined",
            "account_settings",
        )
        extra_kwargs = {
            "username": {"read_only": True},
            "email": {"read_only": True},
            "date_joined": {"read_only": True},
            "first_name": {"allow_blank": False, "required": True},
        }


class AccountSettingsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AccountSettings
        fields = (
            "show_last_seen",
            "show_read_receipts",
            "allow_to_add_groups",
            "allow_private_messages_to_non_contacts",
            "push_notifications_enabled",
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
