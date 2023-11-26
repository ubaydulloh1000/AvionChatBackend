import json
from channels.generic.websocket import AsyncWebsocketConsumer

from . import utils, db_operations
from apps.chat.serializers import MessageDetailSerializer


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
        elif event_type == utils.ReceiveMessageEventTypesEnum.CHAT_SEND_MESSAGE.value:
            chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
            sender = self.scope["user"]
            receiver_id = text_data_json.get("receiver_id", None)
            message_type = text_data_json.get("message_type")
            message_content = text_data_json.get("message_text")

            chat = await db_operations.get_chat_by_id(chat_id)
            if receiver_id:
                receiver = await db_operations.get_user_by_pk(receiver_id)
            else:
                receiver = None

            chat_permittable = await db_operations.check_chat_is_permitted(chat, sender)
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
                "EVENT_TYPE": utils.SendMessageEventTypesEnum.CHAT_SEND_MESSAGE.value,
                "message": MessageDetailSerializer(msg).data
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
        elif event_type == utils.ReceiveMessageEventTypesEnum.PRIVATE_CHAT_SEE_MESSAGE.value:
            msg = await db_operations.mark_message_as_read(
                mid=text_data_json["message_id"],
                user_id=self.scope["user"].id
            )
            event = {
                "type": self.send_private_chat_message.__name__,
                "EVENT_TYPE": utils.SendMessageEventTypesEnum.PRIVATE_CHAT_SEE_MESSAGE.value,
                "message": msg
            }
            await self.channel_layer.group_send(
                self.room_group_name, event
            )
        elif event_type == utils.ReceiveMessageEventTypesEnum.PRIVATE_CHAT_EDIT_MESSAGE.value:
            msg = await db_operations.update_message_by_id(
                msg_id=text_data_json["message_id"],
                user_id=self.scope["user"].id,
                new_content=text_data_json["message_text"]
            )
            event = {
                "type": self.send_private_chat_message.__name__,
                "EVENT_TYPE": utils.SendMessageEventTypesEnum.PRIVATE_CHAT_EDIT_MESSAGE.value,
                "message": msg,
            }
            await self.channel_layer.group_send(
                self.room_group_name, event
            )
        elif event_type == utils.ReceiveMessageEventTypesEnum.PRIVATE_CHAT_MESSAGE_DELETE.value:
            message_id = text_data_json.get("message_id")
            if not message_id or not isinstance(message_id, int):
                return
            msg = await db_operations.get_message_by_id(message_id)
            if not msg:
                return
            is_deleted = await db_operations.soft_delete_message(msg=msg, user=self.scope["user"])
            if not is_deleted:
                return
            event = {
                "type": self.send_private_chat_message.__name__,
                "EVENT_TYPE": utils.SendMessageEventTypesEnum.PRIVATE_CHAT_MESSAGE_DELETE.value,
                "msg_id": msg.id
            }
            await self.channel_layer.group_send(self.room_group_name, event)

    async def send_online_offline_event(self, event):
        await self.send(text_data=json.dumps(event))

    async def send_private_chat_message(self, event):
        await self.send(text_data=json.dumps(event))
