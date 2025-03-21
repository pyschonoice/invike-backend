from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    SocialLoginView,
    TokenRefreshView,
    UserProfileView,
    ProfileUpdateView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('social-login/', SocialLoginView.as_view(), name='social-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),
]