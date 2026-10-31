from django.urls import path
from user import views

app_name = 'user'

urlpatterns = [
  path('', views.list_users),
  path('/register', views.register),
  path('/login', views.login),
  path('/<uuid:id>', views.user_detail),
]
