from django.core.validators import EmailValidator
from rest_framework import serializers
from apps.accounts import models
from django.contrib.auth.password_validation import validate_password


class PasswordField(serializers.CharField):
    """ Serializer field for password. """

    def __init__(self, *args, **kwargs):
        kwargs["style"] = {"input_type": "password"}
        kwargs["write_only"] = True
        super(PasswordField, self).__init__(*args, **kwargs)

    def to_internal_value(self, data):
        validate_password(data)
        return super(PasswordField, self).to_internal_value(data)


class UsernameField(serializers.CharField):
    """ Serializer field for username. """

    def __init__(self, *args, **kwargs):
        kwargs["validators"] = [models.UserNameValidator()]
        super(UsernameField, self).__init__(*args, **kwargs)

    def to_internal_value(self, data):
        data = data.lower()
        if models.User.objects.filter(username=data).exists():
            raise serializers.ValidationError(
                "The username is already taken."
            )
        return super(UsernameField, self).to_internal_value(data)


class EmailField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        kwargs["validators"] = [EmailValidator()]
        super(EmailField, self).__init__(*args, **kwargs)

    def to_internal_value(self, data):
        data = data.lower()
        if models.User.objects.filter(email=data).exists():
            raise serializers.ValidationError(
                "The email is already registered."
            )
        return super(EmailField, self).to_internal_value(data)
