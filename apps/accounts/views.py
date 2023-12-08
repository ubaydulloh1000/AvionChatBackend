from rest_framework import generics, permissions, status, views, parsers
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.accounts.models import User
from . import serializers


class UserRegisterAPIView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()
    serializer_class = serializers.UserRegisterSerializer
    queryset = User.objects.all()


class UserRegisterConfirmAPIView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()
    serializer_class = serializers.UserRegisterConfirmSerializer


class AccountDetailUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    This endpoint retrieves the account details of the currently logged-in user.
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.AccountDetailUpdateSerializer
    http_method_names = ["get", "patch"]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def get_object(self):
        return self.request.user


class AccountSettingsDetailUpdateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.AccountSettingsUpdateSerializer

    def get_object(self):
        return self.request.user.account_settings


check_username_manual_parameters = [
    openapi.Parameter(
        name="username",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description="Username to check",
    ),
]


class CheckUsernameAvailableView(views.APIView):
    @swagger_auto_schema(manual_parameters=check_username_manual_parameters)
    def get(self, *args, **kwargs):
        username = self.request.query_params.get("username", None)
        resp_data = {
            "is_available": User.check_is_username_available(username)
        }
        return Response(data=resp_data, status=status.HTTP_200_OK)


class UserListAPIView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.UserListSerializer
    queryset = User.objects.all()
    search_fields = ("username", "email", "first_name", "last_name")

    def get_queryset(self):
        return self.queryset.exclude(id=self.request.user.id)


class UserProfileAPIView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.UserProfileSerializer
    queryset = User.objects.all()
