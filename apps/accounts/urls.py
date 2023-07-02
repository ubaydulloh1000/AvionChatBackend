from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from . import views


urlpatterns = [
    path('login/', LoginView.as_view(template_name='accounts/login.html', success_url="chat/"), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('list/search/', views.user_list, name='user_list'),
]
