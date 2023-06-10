from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as _UserManager


class UserManager(_UserManager):
    pass


class User(AbstractUser):
    class Meta:
        db_table = "auth_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    objects = UserManager()

    def __str__(self):
        return self.username
