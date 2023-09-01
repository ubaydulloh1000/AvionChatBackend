from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

app_name = 'accounts'

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
        views.UserCreateAPIView.as_view(),
        name="register",
    ),
    path(
        "me/",
        views.AccountDetailAPIView.as_view(),
        name="account_detail",
    ),
    path(
        "check-username-available/",
        views.CheckUsernameAvailableView.as_view(),
        name="check_username_available",
    )
]
