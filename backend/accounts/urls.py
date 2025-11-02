from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import SignUpView, LoginView, UserView, LogoutView

urlpatterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/signup/", SignUpView.as_view(), name="signup"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/user/", UserView.as_view(), name="user"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
]



from .views import (
    list_available_permissions,
    manage_user_permissions,
    list_role_permissions,
    update_role_permissions,
)

urlpatterns += [
    # Gestión de permisos
    path("permissions/available", list_available_permissions, name="available_permissions"),
    path("users/<int:user_id>/permissions", manage_user_permissions, name="user_permissions"),
    path("roles/<str:role>/permissions", list_role_permissions, name="role_permissions"),
    path("roles/<str:role>/permissions/update", update_role_permissions, name="update_role_permissions"),
]
