from django.urls import path
from . import views

app_name = 'promotions'

urlpatterns = [
    path('', views.campaigns_list, name='campaigns'),
    path('<int:pk>/', views.campaign_detail, name='campaign_detail'),
    path('task/<int:task_id>/join/', views.join_task, name='join_task'),
    path('task/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('campaign/<int:campaign_id>/claim/', views.claim_reward, name='claim_reward'),
]
