from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as _UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(_UserManager):
    pass


class User(AbstractUser):
    class Meta:
        db_table = "auth_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    objects = UserManager()

    avatar = models.ImageField(verbose_name=_("Avatar"), upload_to='accounts/avatars/%Y/%m', null=True, blank=True)

    def __str__(self):
        return self.username
