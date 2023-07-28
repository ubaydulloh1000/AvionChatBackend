from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("say_hello/<int:user_id>/", views.say_hello, name="say_hello"),
]
