from django.contrib.auth.models import User
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.users.serializers import UserSerializer, UserListSerializer


class GetAllUsersView(GenericAPIView):
    serializer_class = UserListSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def get(self, request: Request) -> Response:
        users = User.objects.all()
        return Response(self.get_serializer(users, many=True).data)


class RegisterUserView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create user
        user = User.objects.create_user(**serializer.validated_data)

        # Generate tokens using the same logic as TokenObtainPairView
        token_serializer = TokenObtainPairSerializer(
            data={
                "username": user.username,
                "password": request.data["password"],  # must come from raw request
            }
        )
        token_serializer.is_valid(raise_exception=True)

        return Response(token_serializer.validated_data)
