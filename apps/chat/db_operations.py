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
def get_user_by_pk(pk: int) -> Awaitable[Optional[AbstractBaseUser]]:
    return User.objects.filter(pk=pk).first()


@database_sync_to_async
def create_message(chat: models.Chat, sndr: User, rpt: User, m_type: str, content) -> Awaitable[models.Message]:
    match m_type:
        case utils.MessageTypeEnum.TEXT.value:
            msg = create_text_message(chat, sndr, rpt, content)
        case utils.MessageTypeEnum.FILE.value:
            msg = create_file_message(chat, sndr, rpt, content)
        case _:
            raise ValueError("Unknown message type")
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
    else:
        return None


@database_sync_to_async
def mark_message_as_read(mid: int) -> Awaitable[None]:
    return Message.objects.filter(id=mid).update(is_seen=True, seen_at=timezone.now())


@database_sync_to_async
def get_unread_count(sender, recipient) -> Awaitable[int]:
    return Message.get_unread_count_for_private_chat(sender, recipient)
