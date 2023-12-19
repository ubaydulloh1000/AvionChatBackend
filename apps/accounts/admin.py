from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from django.utils.translation import gettext_lazy as _
from django.apps import apps

from django.contrib.auth.models import Group
from apps.base.admin import BaseAdmin
from apps.accounts import models

User = get_user_model()

admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    pass


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("id", "username", "email", "is_staff", "is_active", "date_joined")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "avatar")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined", "is_online", "last_seen_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
    )


@admin.register(models.AccountSettings)
class AccountSettingsAdmin(BaseAdmin):
    pass


@admin.register(models.UserConfirmationCode)
class Admin(admin.ModelAdmin):
    list_display = ("id", "user", "code_type", "code", "expire_at", "attempts",)
    list_display_links = ("id", "user",)
    list_filter = ("user", "code_type",)
