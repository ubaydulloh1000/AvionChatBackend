from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("list/", views.chat_list, name="chat-list"),
    path("<str:room_name>/", views.room, name="room"),
]
