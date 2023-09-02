from enum import Enum
from dataclasses import dataclass


class SendMessageEventTypesEnum(Enum):
    PRIVATE_CHAT_ONLINE_STATUS = 'private_chat_online_status'
    PRIVATE_CHAT_TYPING = 'private_chat_typing'
    PRIVATE_CHAT_STOPPED_TYPING = 'private_chat_stopped_typing'
    PRIVATE_CHAT_SEND_MESSAGE = 'private_chat_send_message'


class ReceiveMessageEventTypesEnum(Enum):
    CHECK_PRIVATE_CHAT_USER_ONLINE = 'check_private_chat_user_online'
    PRIVATE_CHAT_SEND_MESSAGE = 'private_chat_send_message'


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
