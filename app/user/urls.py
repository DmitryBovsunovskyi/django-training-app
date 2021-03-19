from django.urls import path

from user import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

app_name = 'user'

urlpatterns = [
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('email-verify/', views.VerifyEmailView.as_view(), name='email-verify'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('request-reset-email/', views.PasswordResetEmail.as_view(), name='request-reset-email'),
    path('password-reset/<uidb64>/<token>/', views.PasswordTokenCheckApi.as_view(), name='password-reset-confirm'),
    path('password-reset-complete/', views.SetNewPasswordView.as_view(), name='password-reset-complete')
]
