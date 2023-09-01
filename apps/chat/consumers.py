import json
from channels.generic.websocket import AsyncWebsocketConsumer

from asgiref.sync import sync_to_async
from apps.chat.models import Chat, Message
from . import utils


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

        self.room_name = self.scope["url_route"]["kwargs"]["chat_id"]
        self.room_group_name = "chat_%s" % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
        except json.JSONDecodeError:
            return

        action = text_data_json.get("action", None)
        match action:
            case utils.ChatActionEnum.MESSAGE_SEND.value:
                # MESSAGE: {
                #   "action": "message_send",
                #   "recipient": 123,
                #   "message_type": "text",
                #   "message": "Hello world!",
                # }
                pass

            case utils.ChatActionEnum.MESSAGE_SEE.value:
                pass
            case _:
                # JUST DO NOTHING
                return

        message = text_data_json["message"]

        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": self.send_private_chat_message.__name__,
                "action": text_data_json["action"],
                "receiver_id": text_data_json["receiver"],
                "message_type": text_data_json["message_type"],
                "message": message
            }
        )

    async def send_private_chat_message(self, event):
        action = event["action"]
        sender = self.scope["user"]
        receiver_id = event["receiver_id"]
        message_type = event["message_type"]
        message = event["message"]

        await self.send(
            text_data=json.dumps(
                {
                    "chat_type": Chat.ChatTypeChoices.PRIVATE.value,
                    "action": action,
                    "sender_id": sender.id,
                    "receiver_id": receiver_id,
                    "message_type": message_type,
                    "message": message
                }
            )
        )

    @sync_to_async
    def save_message_to_database(self, message, user, chat_id):
        Message.objects.create(sender=user, chat_id=chat_id, content=message)
