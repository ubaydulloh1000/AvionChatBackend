from django.db import models
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from apps.accounts.admin import User
from apps.chat.models import Message, Chat


@login_required
def index(request, *args, **kwargs):
    current_chat = None
    current_chat_query = request.GET.get("current_chat_id")
    chat_list_search = request.GET.get("cht_q")
    chat_queryset = request.user.chats.all()

    if chat_list_search:
        chat_queryset = chat_queryset.filter(
            models.Q(name__icontains=chat_list_search) |
            models.Q(user1__username__icontains=chat_list_search) |
            models.Q(user2__username__icontains=chat_list_search) |
            models.Q(user1__first_name__icontains=chat_list_search) |
            models.Q(user2__first_name__icontains=chat_list_search) |
            models.Q(user1__last_name__icontains=chat_list_search) |
            models.Q(user2__last_name__icontains=chat_list_search)
        )

    chat_queryset = chat_queryset.annotate(
        last_message_date=models.Max("messages__created_at"),
        last_message_content=models.Subquery(
            Message.objects.filter(chat=models.OuterRef('pk')).order_by('-created_at').values("content")[:1]
        ),
        last_message_is_owner_username=models.Subquery(
            Message.objects.filter(chat=models.OuterRef('pk')).order_by('-created_at').values("sender__username")[:1]
        ),
        last_message_is_seen=models.Subquery(
            Message.objects.filter(chat=models.OuterRef('pk')).order_by('-created_at').values("is_seen")[:1]
        ),
    )
    if current_chat_query:
        current_chat = chat_queryset.filter(id=current_chat_query).first()

    current_chat_message_queryset = current_chat.messages.all() if current_chat else None

    context = {
        "chat_queryset": chat_queryset.order_by("-last_message_date"),
        "current_chat": current_chat,
        "current_chat_message_queryset": current_chat_message_queryset,
    }
    return render(request, "chat/index.html", context)


@login_required
def chat_list(request):
    return render(request, "chat/chats_list.html")


@login_required
def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})


@login_required
def say_hello(request, user_id):
    user = User.objects.get(id=user_id)

    chat, _ = Chat.objects.get_or_create(
        type=Chat.ChatTypeChoices.PRIVATE,
        name=request.user.username + " -> " + user.username,
        owner=request.user,
        user1=request.user,
        user2=user,
    )
    chat.members.add(request.user)
    chat.members.add(user)

    Message.objects.create(
        chat=chat,
        sender=request.user,
        content="Hello",
        type=Message.MessageTypeChoices.TEXT,
    )
    return redirect("index")
