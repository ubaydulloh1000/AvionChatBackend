from django.core.management.base import BaseCommand
from apps.chat.models import ChatMembership, GroupMembership, ChannelSubscription, PrivateChatMembership


class Command(BaseCommand):
    help = "Fix chat membership"

    def handle(self, *args, **options):
        for group_membership in GroupMembership.objects.all():
            try:
                chat_membership = ChatMembership.objects.get(
                    chat_id=group_membership.group.id,
                    user_id=group_membership.user.id
                )
            except ChatMembership.DoesNotExist:
                chat_membership = ChatMembership.objects.create(
                    chat_id=group_membership.group.id,
                    user_id=group_membership.user.id
                )
            chat_membership.is_archived = group_membership.is_archived
            chat_membership.is_muted = group_membership.is_muted
            chat_membership.save()

        for channel_subscription in ChannelSubscription.objects.all():
            try:
                chat_membership = ChatMembership.objects.get(
                    chat_id=channel_subscription.channel_id,
                    user_id=channel_subscription.subscriber_id
                )
            except ChatMembership.DoesNotExist:
                chat_membership = ChatMembership.objects.create(
                    chat_id=channel_subscription.channel_id,
                    user_id=channel_subscription.subscriber_id
                )
            chat_membership.is_archived = channel_subscription.is_archived
            chat_membership.is_muted = channel_subscription.is_muted
            chat_membership.save()

        for private_chat_membership in PrivateChatMembership.objects.all():
            try:
                chat_membership = ChatMembership.objects.get(
                    chat_id=private_chat_membership.chat.id,
                    user_id=private_chat_membership.user.id
                )
            except ChatMembership.DoesNotExist:
                chat_membership = ChatMembership.objects.create(
                    chat_id=private_chat_membership.chat.id,
                    user_id=private_chat_membership.user.id
                )
            chat_membership.is_archived = private_chat_membership.is_archived
            chat_membership.is_muted = private_chat_membership.is_muted
            chat_membership.save()
