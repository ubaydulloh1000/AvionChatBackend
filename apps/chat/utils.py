from enum import Enum
from dataclasses import dataclass


class SendMessageEventTypesEnum(Enum):
    PRIVATE_CHAT_ONLINE_STATUS = 'private_chat_online_status'
    PRIVATE_CHAT_USER_TYPING_STATUS = 'private_chat_user_typing_status'
    CHAT_SEND_MESSAGE = 'private_chat_send_message'
    PRIVATE_CHAT_SEE_MESSAGE = 'private_chat_see_message'
    PRIVATE_CHAT_EDIT_MESSAGE = 'private_chat_edit_message'
    PRIVATE_CHAT_MESSAGE_DELETE = 'private_chat_message_delete'

    GROUP_CHAT_SEND_MESSAGE = 'group_chat_send_message'


class ReceiveMessageEventTypesEnum(Enum):
    CHECK_PRIVATE_CHAT_USER_ONLINE = 'check_private_chat_user_online'
    PRIVATE_CHAT_USER_TYPING_STATUS = 'private_chat_user_typing_status'
    CHAT_SEND_MESSAGE = 'private_chat_send_message'
    PRIVATE_CHAT_SEE_MESSAGE = 'private_chat_see_message'
    PRIVATE_CHAT_EDIT_MESSAGE = 'private_chat_edit_message'
    PRIVATE_CHAT_MESSAGE_DELETE = 'private_chat_message_delete'


@dataclass
class MessageDataClass:
    id: int
    chat_id: int
    sender_id: int
    recipient_id: int
    text: str
    file: str
    is_seen: bool
    seen_at: str


class UserActionEnum(Enum):
    CHAT_CREATE = 'chat_create'
    CHAT_DELETE = 'chat_delete'


class ChatActionEnum(Enum):
    MESSAGE_SEND = 'message_send'
    MESSAGE_SEE = 'message_see'


class MessageTypeEnum(Enum):
    TEXT = 'text'
    FILE = 'file'
