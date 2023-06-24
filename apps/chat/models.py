from django.db import models
from apps.base.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _


class ChatGroup(TimeStampedModel):
    class Meta:
        db_table = "chat_group"

    name = models.CharField(verbose_name=_("Name"), max_length=255)
    owner = models.ForeignKey(
        verbose_name=_("Owner"),
        to="accounts.User",
        related_name="owned_chat_groups",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class PrivateChat(TimeStampedModel):
    class Meta:
        db_table = "private_chat"

    user1 = models.ForeignKey(
        verbose_name=_("User 1"),
        to="accounts.User",
        related_name="private_chats1",
        on_delete=models.CASCADE,
    )
    user2 = models.ForeignKey(
        verbose_name=_("User 2"),
        to="accounts.User",
        related_name="private_chats2",
        on_delete=models.CASCADE,
    )


class Message(TimeStampedModel):
    class MessageTypeChoices(models.TextChoices):
        TEXT = "TEXT", _("Text")
        IMAGE = "IMAGE", _("Image")
        VIDEO = "VIDEO", _("Video")
        AUDIO = "AUDIO", _("Audio")

    private_chat = models.ForeignKey(
        verbose_name=_("Private Chat"),
        to="chat.PrivateChat",
        related_name="messages",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    group = models.ForeignKey(
        verbose_name=_("Group"),
        to="chat.ChatGroup",
        related_name="messages",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    type = models.CharField(
        verbose_name=_("Type"),
        max_length=255,
        choices=MessageTypeChoices.choices,
        default=MessageTypeChoices.TEXT,
    )
    content = models.TextField(verbose_name=_("Content"))

    def __str__(self):
        return self.type
