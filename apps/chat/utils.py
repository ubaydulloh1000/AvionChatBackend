from enum import Enum
from dataclasses import dataclass


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
