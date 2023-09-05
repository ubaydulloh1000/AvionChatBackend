from django.db import models
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class PrivateChatMembershipQuerySet(models.QuerySet):
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


class GroupMembershipQuerySet(models.QuerySet):
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


class ChannelSubscriptionQuerySet(models.QuerySet):
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
