from django.urls import path
from . import views

app_name = 'tasks'  # ← THIS IS THE MISSING LINE


urlpatterns = [
    path('feed/', views.task_feed, name='task_feed'),
    path('start_task/<int:task_id>/', views.start_task, name='start_task'),
    path('create/', views.task_basic_info, name='create_task'),
    path('create/likert/<int:task_id>/', views.add_likert_items, name='add_likert_items'),
    path('create/fc/<int:task_id>/', views.add_fc_items, name='add_fc_items'),
    path('preview/<int:task_id>/', views.task_preview, name='task_preview'),
    path('do_task/<int:task_id>/likert/<int:item_index>/', views.do_likert_task, name='do_likert_task'),
    path('do_task/<int:task_id>/fc/<int:item_index>/', views.do_fc_task, name='do_fc_task'),
    path('end_task/<int:task_id>/', views.end_task, name='end_task'),
]

