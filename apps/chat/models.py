from django.db import models
from apps.base.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _


class Chat(TimeStampedModel):
    class ChatTypeChoices(models.TextChoices):
        PRIVATE = "PRIVATE", _("Private")
        GROUP = "GROUP", _("Group")
        CHANNEL = "CHANNEL", _("Channel")

    class Meta:
        db_table = "chat"

    type = models.CharField(
        verbose_name=_("Type"),
        max_length=255,
        choices=ChatTypeChoices.choices,
        null=True,
    )
    name = models.CharField(verbose_name=_("Name"), max_length=255)
    owner = models.ForeignKey(
        verbose_name=_("Owner"),
        to="accounts.User",
        related_name="owned_chat_groups",
        on_delete=models.CASCADE,
    )
    members = models.ManyToManyField(
        verbose_name=_("Members"),
        to="accounts.User",
        related_name="chats",
        blank=True,
    )
    user1 = models.ForeignKey(
        verbose_name=_("User 1"),
        to="accounts.User",
        related_name="user1_chats",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    user2 = models.ForeignKey(
        verbose_name=_("User 2"),
        to="accounts.User",
        related_name="user2_chats",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class Message(TimeStampedModel):
    class MessageTypeChoices(models.TextChoices):
        TEXT = "TEXT", _("Text")
        IMAGE = "IMAGE", _("Image")
        VIDEO = "VIDEO", _("Video")
        AUDIO = "AUDIO", _("Audio")

    chat = models.ForeignKey(
        verbose_name=_("Private Chat"),
        to="chat.Chat",
        related_name="messages",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    sender = models.ForeignKey(
        verbose_name=_("Sender"),
        to="accounts.User",
        related_name="messages",
        on_delete=models.CASCADE,
        null=True,
    )
    type = models.CharField(
        verbose_name=_("Type"),
        max_length=255,
        choices=MessageTypeChoices.choices,
        default=MessageTypeChoices.TEXT,
    )
    content = models.TextField(verbose_name=_("Content"))
    is_seen = models.BooleanField(verbose_name=_("Is Seen"), default=False)
    seen_at = models.DateTimeField(verbose_name=_("Seen At"), null=True, blank=True)

    def __str__(self):
        return self.type
