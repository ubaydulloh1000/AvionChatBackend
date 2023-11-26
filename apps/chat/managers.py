from django.db import models
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class ChatMembershipQuerySet(models.QuerySet):
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


class MessageQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_deleted=False, deleted_at__isnull=True)
