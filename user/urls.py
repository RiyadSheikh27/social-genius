from django.urls import path
from user.views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView
)

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('social-login/', social_signup_signup, name='social_signup_signup'),
    path('signin/', MyTokenObtainPairView.as_view(), name='signin'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('signup/send-otp/', send_otp, name='signup_send_otp'),
    path('otp-code-verified/', otp_code_verified, name='otp_code_verified'),
    path('profile/', user_profile, name='user_profile'),
    path('reset_send_otp/', reset_send_otp, name='reset_send_otp'),
    path('reset_new_password/', reset_new_password, name='reset_new_password'),
    path('changed_password/', changed_password, name='changed_password'),
    path('account/delete/', delete_account, name='delete_account'),

]