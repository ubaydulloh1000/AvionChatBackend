import json
from channels.generic.websocket import AsyncWebsocketConsumer

from asgiref.sync import sync_to_async
from apps.chat.models import Chat, Message
from . import utils, db_operations
from apps.chat.serializers import MessageListSerializer


class UserConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = "None"
        self.user_group_name = "None"

    async def connect(self):
        self.user_id = str(self.scope["url_route"]["kwargs"]["user_id"])
        if self.user_id.isdigit() and int(self.user_id) != self.scope["user"].id:
            await self.close()
            return
        self.user_group_name = "user_group_%s" % self.user_id

        await self.channel_layer.group_add(
            self.user_group_name, self.user_id
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group_name, self.user_id
        )

    async def receive(self, text_data):
        json_data = json.loads(text_data)
        action = json_data["action"]

        match action:
            case utils.UserActionEnum.CHAT_CREATE.value:
                print(utils.UserActionEnum.CHAT_CREATE)
            case utils.UserActionEnum.CHAT_DELETE.value:
                print(utils.UserActionEnum.CHAT_DELETE)
            case _:
                print("Unknown action")


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = "None"
        self.room_group_name = "None"

    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
            return
        chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        chat = await db_operations.get_chat_by_id(chat_id)
        if chat is None:
            await self.close()
            return

        if not await db_operations.check_chat_is_permitted(chat, self.scope["user"]):
            await self.close()
            return

        self.room_name = 'private_chat_{chat_id}'.format(chat_id=self.scope["url_route"]["kwargs"]["chat_id"])
        self.room_group_name = "group_%s" % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()

    async def accept(self, subprotocol=None):
        await super().accept(subprotocol=subprotocol)
        await db_operations.set_user_online(self.scope["user"])
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": self.send_online_offline_event.__name__,
                "EVENT_TYPE": utils.SendMessageEventTypesEnum.PRIVATE_CHAT_ONLINE_STATUS.value,
                "is_online": True,
                "user_id": self.scope["user"].id
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )
        await db_operations.set_user_offline(self.scope["user"])
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": self.send_online_offline_event.__name__,
                "EVENT_TYPE": utils.SendMessageEventTypesEnum.PRIVATE_CHAT_ONLINE_STATUS.value,
                "is_online": False,
                "user_id": self.scope["user"].id
            }
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
        except json.JSONDecodeError:
            return

        event_type = text_data_json.get("EVENT_TYPE")
        if event_type == utils.ReceiveMessageEventTypesEnum.CHECK_PRIVATE_CHAT_USER_ONLINE.value:
            user = await db_operations.get_user_by_pk(text_data_json["user_id"])
            is_online = await db_operations.user_is_online(user)

            event = {
                "type": self.send_online_offline_event.__name__,
                "EVENT_TYPE": utils.SendMessageEventTypesEnum.PRIVATE_CHAT_ONLINE_STATUS.value,
                "is_online": is_online,
                "user_id": text_data_json["user_id"]
            }
            await self.channel_layer.group_send(
                self.room_group_name, event
            )
        elif event_type == utils.ReceiveMessageEventTypesEnum.PRIVATE_CHAT_SEND_MESSAGE.value:
            chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
            sender = self.scope["user"]
            receiver_id = text_data_json.get("receiver_id")
            message_type = text_data_json.get("message_type")
            message_content = text_data_json.get("message_text")

            chat = await db_operations.get_chat_by_id(chat_id)
            receiver = await db_operations.get_user_by_pk(receiver_id)

            chat_permittable = await db_operations.check_chat_is_permitted(chat, receiver)
            if not chat_permittable:
                return

            msg = await db_operations.save_message_to_db(
                chat=chat,
                sndr=sender,
                rcpt=receiver,
                msg_type=message_type,
                content=message_content,
            )
            event = {
                "type": self.send_private_chat_message.__name__,
                "EVENT_TYPE": utils.SendMessageEventTypesEnum.PRIVATE_CHAT_SEND_MESSAGE.value,
                "message": MessageListSerializer(msg).data
            }
            await self.channel_layer.group_send(
                self.room_group_name, event
            )
        elif event_type == utils.ReceiveMessageEventTypesEnum.PRIVATE_CHAT_USER_TYPING_STATUS.value:
            event = {
                "type": self.send_private_chat_message.__name__,
                "EVENT_TYPE": utils.SendMessageEventTypesEnum.PRIVATE_CHAT_USER_TYPING_STATUS.value,
                "user_id": text_data_json["user_id"],
                "is_typing": text_data_json["is_typing"]
            }
            await self.channel_layer.group_send(
                self.room_group_name, event
            )

    async def send_online_offline_event(self, event):
        await self.send(text_data=json.dumps(event))

    async def send_private_chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def save_message_to_database(self, message, user, chat_id):
        Message.objects.create(sender=user, chat_id=chat_id, content=message)
