from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users.serializers import (
    LoginUserSerializer,
    RegisterUserSerializer,
    UserListSerializer,
)


class GetAllUsersView(GenericAPIView):
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        users = User.objects.all()
        return Response(self.get_serializer(users, many=True).data)


class RegisterUserView(GenericAPIView):
    serializer_class = RegisterUserSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data.copy()
        data["username"] = data["email"]

        if User.objects.filter(username=data["username"]).exists():
            raise ValidationError({"email": "A user with this email already exists."})

        user = User.objects.create_user(**data)

        token_serializer = TokenObtainPairSerializer(
            data={
                "email": user.email,
                "username": user.email,
                "password": request.data["password"],
            }
        )
        token_serializer.is_valid(raise_exception=True)

        return Response(token_serializer.validated_data)


class LoginUserView(GenericAPIView):
    serializer_class = LoginUserSerializer
    permission_classes = (AllowAny,)

    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_serializer = TokenObtainPairSerializer(
            data={
                "email": serializer.data["email"],
                "username": serializer.data["email"],
                "password": request.data["password"],
            }
        )
        token_serializer.is_valid(raise_exception=True)

        return Response(token_serializer.validated_data)
