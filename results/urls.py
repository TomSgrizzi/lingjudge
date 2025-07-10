from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_results_view, name='my_results'),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
    path('task/<int:task_id>/download/', views.download_task_results, name='download_task_results'),
    path('task/<int:task_id>/edit/', views.task_edit, name='task_edit'),
    path('task/<int:task_id>/delete/', views.task_delete, name='task_delete'),
]
