from django.db import models
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class BaseChatMembershipQuerySet(models.QuerySet):
    def annotate_last_message(self, *, outer_ref_name):
        from apps.chat.models import Message as MessageModel

        base_subquery = MessageModel.objects.filter(chat=models.OuterRef(outer_ref_name)).order_by('-created_at')
        created_subquery = base_subquery.values('created_at')[:1]
        content_subquery = base_subquery.values('content')[:1]
        sender_subquery = base_subquery.values('sender_id')[:1]
        is_seen_subquery = base_subquery.values('is_seen')[:1]

        qs = self.annotate(
            last_message_created_at=models.Subquery(
                created_subquery, output_field=models.DateTimeField()
            ),
            last_message_content=models.Subquery(
                content_subquery, output_field=models.TextField()
            ),
            last_message_sender_id=models.Subquery(
                sender_subquery, output_field=models.IntegerField()
            ),
            last_message_is_seen=models.Subquery(
                is_seen_subquery, output_field=models.BooleanField()
            ),
        )
        return qs


class PrivateChatMembershipQuerySet(BaseChatMembershipQuerySet):
    def search_by_interlocutor(self, search_query, user):
        qs = self.filter(
            models.Q(chat__user1=user, chat__user2__username__icontains=search_query) |
            models.Q(chat__user1=user, chat__user2__first_name__icontains=search_query) |
            models.Q(chat__user1=user, chat__user2__last_name__icontains=search_query) |
            models.Q(chat__user2=user, chat__user1__username__icontains=search_query) |
            models.Q(chat__user2=user, chat__user1__first_name__icontains=search_query) |
            models.Q(chat__user2=user, chat__user1__last_name__icontains=search_query)
        )
        return qs

    def annotate_unseen_messages_count(self, user):
        return self.annotate(
            unseen_messages_count=models.Count(
                models.Case(
                    models.When(
                        models.Q(
                            chat__messages__is_seen=False,
                            chat__messages__recipient=user,
                        ),
                        then=1,
                    )
                )
            )
        )


class GroupMembershipQuerySet(BaseChatMembershipQuerySet):
    def annotate_unseen_messages_count(self, user):
        return self.annotate(
            unseen_messages_count=models.Count(
                models.Case(
                    models.When(
                        models.Q(
                            group__messages__is_seen=False,
                            group__messages__recipient=user,
                        ),
                        then=1,
                    )
                )
            )
        )


class ChannelSubscriptionQuerySet(BaseChatMembershipQuerySet):
    def annotate_unseen_messages_count(self, user):
        return self.annotate(
            unseen_messages_count=models.Count(
                models.Case(
                    models.When(
                        models.Q(
                            channel__messages__is_seen=False,
                            channel__messages__recipient=user,
                        ),
                        then=1,
                    )
                )
            )
        )
