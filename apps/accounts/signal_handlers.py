from django.db.models.signals import post_save
from django.dispatch import receiver
from . import models


@receiver(post_save, sender=models.User)
def create_user_account_settings(sender, instance, created, **kwargs):
    if not hasattr(instance, "account_settings"):
        models.AccountSettings.objects.create(user=instance)
