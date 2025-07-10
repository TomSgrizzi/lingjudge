from django.urls import path
from . import views


urlpatterns = [
    path('', views.public_home, name='public_home'),
]
