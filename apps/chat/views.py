from django.shortcuts import render
from django.views.generic import ListView
from django.views import View
from django.http.response import HttpResponse


def index(request):
    return render(request, "chat/index.html")


def chat_list(request):
    return render(request, "chat/chats_list.html")


def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})
