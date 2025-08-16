"""config URL Configuration"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from todo.views import UserRegistrationView

urlpatterns = [
    path("admin/", admin.site.urls),

    # JWT auth
    path("api/auth/register/", UserRegistrationView.as_view(), name="register"),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Todo app
    path("api/", include("todo.urls")
)]
