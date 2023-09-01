from rest_framework import generics, permissions, status, views
from rest_framework.response import Response

from apps.accounts.models import User
from . import serializers

__all__ = [
    "AccountDetailAPIView",
    "CheckUsernameAvailableView",
]


class UserCreateAPIView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.UserCreateSerializer
    queryset = User.objects.all()


class AccountDetailAPIView(generics.RetrieveAPIView):
    """
    This endpoint retrieves the account details of the currently logged-in user.
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.AccountDetailSerializer

    def get_object(self):
        return self.request.user


class CheckUsernameAvailableView(views.APIView):
    def get(self, request, *args, **kwargs):
        username = request.query_params.get("username", None)
        is_available = True

        if User.objects.filter(username=username).exists():
            is_available = False
        return Response(
            {
                "is_available": is_available
            },
            status=status.HTTP_200_OK,
        )
