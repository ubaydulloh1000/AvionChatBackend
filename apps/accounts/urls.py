from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.views.decorators.cache import cache_page
from . import views

app_name = 'accounts'

ONE_MINUTE = 60
FIVE_MINUTES = 60 * 10
ONE_HOUR = 60 * 60
TWO_HOUR = ONE_HOUR * 2

urlpatterns = [
    path(
        "login/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "register/",
        views.UserRegisterAPIView.as_view(),
        name="register",
    ),
    path(
        "register/confirm/",
        views.UserRegisterConfirmAPIView.as_view(),
        name="register_confirm",
    ),
    path(
        "me/",
        views.AccountDetailAPIView.as_view(),
        name="account_detail",
    ),
    path(
        "check-username-available/",
        cache_page(ONE_MINUTE)(views.CheckUsernameAvailableView.as_view()),
        name="check_username_available",
    ),
    path(
        "list/",
        cache_page(TWO_HOUR)(views.UserListAPIView.as_view()),
        name="user_list",
    ),
    path(
        "profile/<int:pk>/",
        cache_page(FIVE_MINUTES)(views.UserProfileAPIView.as_view()),
        name="user_profile",
    ),
]
