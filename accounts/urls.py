# accounts/urls.py

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginRegisterView.as_view(), name='login_register'),
    path('send-otp/', views.SendOtpView.as_view(), name='send_otp'),
    path('verify-otp/', views.VerifyOtpView.as_view(), name='verify_otp'),
    path('resend-otp/', views.ResendOtpView.as_view(), name='resend_otp'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
