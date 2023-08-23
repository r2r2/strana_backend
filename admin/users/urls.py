from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('check_superuser_auth', views.check_superuser_auth),
]
