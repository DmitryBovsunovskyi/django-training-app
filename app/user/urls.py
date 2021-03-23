from django.urls import path

from user import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'user'

router = DefaultRouter()
router.register('users', views.UserListViewSet)

urlpatterns = [
    path('create/', views.RegisterUserView.as_view(), name='register'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('logout/', views.LogOutAPIView.as_view(), name="logout"),
    path('update/', views.ManageUserView.as_view(), name="update"),
    path('email-verify/', views.VerifyEmailView.as_view(), name='email-verify'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('request-reset-email/', views.PasswordResetEmail.as_view(), name='request-reset-email'),
    path('password-reset/<uidb64>/<token>/', views.PasswordTokenCheckApi.as_view(), name='password-reset-confirm'),
    path('password-reset-complete/', views.SetNewPasswordView.as_view(), name='password-reset-complete')
]
urlpatterns += router.urls
