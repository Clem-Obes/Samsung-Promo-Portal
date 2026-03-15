from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    # Email verification
    path('verify/email/', views.verify_email_page, name='verify_email_page'),
    path('verify/email/resend/', views.resend_email_otp, name='resend_email_otp'),
    path('verify/email/<str:token>/', views.verify_email_link, name='verify_email_link'),
    # Phone verification
    path('verify/phone/', views.verify_phone_page, name='verify_phone_page'),
    path('verify/phone/resend/', views.resend_phone_otp, name='resend_phone_otp'),
]
