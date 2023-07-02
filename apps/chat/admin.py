from django.contrib import admin

from . import models


@admin.register(models.Chat)
class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "created_at", "updated_at")
    list_display_links = ("id", "name")


@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "chat", "sender", "type", "created_at", "updated_at")
