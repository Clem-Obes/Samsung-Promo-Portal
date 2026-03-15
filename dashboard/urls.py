from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('tasks/', views.tasks_view, name='tasks'),
    path('referrals/', views.referrals_view, name='referrals'),
    path('rewards/', views.rewards_view, name='rewards'),
    # Certificates
    path('certificates/', views.certificates_list, name='certificates'),
    path('certificate/<int:pk>/', views.certificate_view, name='certificate_view'),
    path('certificate/<int:pk>/print/', views.certificate_print, name='certificate_print'),
    path('certificate/verify/<str:hash_prefix>/', views.certificate_verify, name='certificate_verify'),
]
