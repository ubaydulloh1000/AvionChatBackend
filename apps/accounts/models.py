import re
import secrets
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as _UserManager
from django.core.validators import RegexValidator, FileExtensionValidator
from django.db import models
from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.base.models import TimeStampedModel


def default_username():
    import uuid

    username = uuid.uuid4().hex[:12]
    while User.objects.filter(username=username).exists():
        username = uuid.uuid4().hex[:12]
    return username


class UserNameValidator(RegexValidator):
    regex = r"^[a-zA-Z0-9_]{4,100}$"
    message = _(
        "Enter a valid username. This value may contain only letters, "
        "numbers, and underscore(_) character."
    )
    flags = re.ASCII


class UserManager(_UserManager):
    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    class Meta:
        db_table = "auth_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    objects = UserManager()

    username_validator = UserNameValidator()
    username = models.CharField(
        _("username"),
        max_length=50,
        unique=True,
        help_text=_(
            "Required. 50 characters or fewer. Letters, digits and a-z,A-Z,0-9_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
        default=default_username
    )
    email = models.EmailField(_("email address"), unique=True)
    avatar = models.ImageField(
        verbose_name=_("Avatar"),
        upload_to='accounts/avatars/%Y/%m',
        null=True,
        blank=True
    )
    is_online = models.BooleanField(verbose_name=_("Is Online"), default=False)
    last_seen_at = models.DateTimeField(verbose_name=_("Last Seen At"), null=True, blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username

    @classmethod
    def check_is_username_available(cls, username):
        if not username:
            return False
        if 3 <= len(username) <= 30 and not cls.objects.filter(username=username).exists():
            return True
        return False


class AccountSettings(TimeStampedModel):
    class Meta:
        db_table = "account_settings"
        verbose_name = _("Account Settings")
        verbose_name_plural = _("Account Settings")

    user = models.OneToOneField(
        verbose_name=_("User"),
        to="accounts.User",
        related_name="account_settings",
        on_delete=models.CASCADE,
    )
    show_last_seen = models.BooleanField(verbose_name=_("Show Last Seen"), default=True)
    show_read_receipts = models.BooleanField(
        verbose_name=_("Show Read Receipts"),
        help_text=_("Show Read Receipts in Private Chats"),
        default=True,
    )
    allow_to_add_groups = models.BooleanField(verbose_name=_("Allow to Add Groups"), default=True)
    allow_private_messages_to_non_contacts = models.BooleanField(
        verbose_name=_("Allow Private Messages to Non Contacts"), default=True
    )

    push_notifications_enabled = models.BooleanField(
        verbose_name=_("Push Notifications Enabled"), default=True
    )

    def __str__(self):
        return f"{self.user}"


class UserConfirmationCode(TimeStampedModel):
    class Meta:
        db_table = "user_confirmation_code"
        verbose_name = _("User Confirmation Code")
        verbose_name_plural = _("User Confirmation Codes")

    class CodeTypeChoices(models.TextChoices):
        GENERAL = "general", _("General")
        REGISTER = "register", _("Register")
        RESET_PASSWORD = "reset_password", _("Reset password")

    user = models.ForeignKey(
        verbose_name=_("User"),
        to="accounts.User",
        related_name="confirmation_codes",
        on_delete=models.CASCADE,
    )
    code_type = models.CharField(
        verbose_name=_("Code Type"),
        max_length=20,
        choices=CodeTypeChoices.choices,
        default=CodeTypeChoices.GENERAL,
    )
    token = models.CharField(verbose_name=_("Token"), max_length=255, default=secrets.token_urlsafe, unique=True)
    code = models.CharField(verbose_name=_("Code"), max_length=6)
    expire_at = models.DateTimeField(verbose_name=_("Expire At"))
    attempts = models.PositiveSmallIntegerField(verbose_name=_("Attempts"), default=0)

    def __str__(self):
        return f"{self.user} - {self.code}"

    @property
    def is_expired(self):
        return self.expire_at < timezone.now()
