from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('subscribe/<slug:plan_slug>/', views.subscribe, name='subscribe'),
    path('verify/', views.verify_payment, name='verify_payment'),
    path('success/', views.payment_success, name='payment_success'),
]
