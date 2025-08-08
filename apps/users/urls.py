from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.views import RegisterUserView, GetAllUsersView, LoginUserView

urlpatterns = [
    path("users", GetAllUsersView.as_view(), name="get_all_users"),
    path("users/register", RegisterUserView.as_view(), name="token_register"),
    path("users/login", LoginUserView.as_view(), name="token_register"),
    path("users/token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("users/token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
]
