from channels.db import database_sync_to_async
from typing import Set, Awaitable, Optional, Tuple
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone

from apps.accounts.models import (
    User,
)
from apps.chat import models
from apps.chat.models import Message
from . import utils


@database_sync_to_async
def get_chat_by_id(chat_id: int) -> Awaitable[Optional[models.Chat]]:
    return models.Chat.objects.filter(id=chat_id).first()


@database_sync_to_async
def check_chat_is_permitted(chat: models.Chat, user: User) -> bool:
    return chat.is_permitted(user)


@database_sync_to_async
def get_user_by_pk(pk: int) -> Awaitable[Optional[AbstractBaseUser]]:
    return User.objects.filter(pk=pk).first()


@database_sync_to_async
def user_is_online(user: User) -> bool:
    return user.is_online


@database_sync_to_async
def set_user_online(user: User) -> Awaitable[None]:
    user.is_online = True
    user.last_seen_at = timezone.now()
    return user.save()


@database_sync_to_async
def set_user_offline(user: User) -> Awaitable[None]:
    user.is_online = False
    user.last_seen_at = timezone.now()
    return user.save()


@database_sync_to_async
def save_message_to_db(chat: models.Chat, sndr: User, rcpt: User, msg_type, content) -> Awaitable[models.Message]:
    if msg_type == Message.MessageTypeChoices.TEXT.value:
        msg = Message(
            chat=chat,
            sender=sndr,
            recipient=rcpt,
            type=msg_type,
            content=content,
        )
    else:
        # TODO: handle file messages, etc.
        return
    msg.save()
    return msg


@database_sync_to_async
def create_text_message(chat: models.Chat, sndr: User, rpt: User, text: str) -> Awaitable[models.Message]:
    try:
        msg = Message.objects.create(
            chat=chat,
            sender=sndr,
            recipient=rpt,
            text=text,
        )
    except Exception as e:
        print(e)
        raise e
    return msg


@database_sync_to_async
def create_file_message(chat: models.Chat, sndr: User, rpt: User, file: str) -> Awaitable[models.Message]:
    try:
        msg = Message.objects.create(
            chat=chat,
            sender=sndr,
            recipient=rpt,
            file=file,
        )
    except Exception as e:
        print(e)
        raise e
    return msg


@database_sync_to_async
def get_message_by_id(mid: int) -> Message | None:
    msg: Optional[models.Message] = models.Message.objects.filter(id=mid).first()
    if msg:
        return msg
    return None


@database_sync_to_async
def mark_message_as_read(mid: int, user_id: int) -> Awaitable[models.Message | None]:
    msg = Message.objects.filter(id=mid, recipient_id=user_id).first()
    if not msg:
        return None
    if msg.is_seen:
        return msg
    msg.is_seen = True
    msg.seen_at = timezone.now()
    msg.save(update_fields=['is_seen', 'seen_at'])
    return msg


@database_sync_to_async
def update_message_by_id(msg_id: int, user_id: int, new_content: str) -> Awaitable[models.Message | None]:
    msg = Message.objects.filter(id=msg_id, sender_id=user_id).first()
    if not msg:
        return None
    if msg.content == new_content:
        return msg
    msg.content = new_content
    msg.is_edited = True
    msg.save(update_fields=['content', 'is_edited'])
    return msg


@database_sync_to_async
def get_unread_count(sender, recipient) -> Awaitable[int]:
    return Message.get_unread_count_for_private_chat(sender, recipient)
