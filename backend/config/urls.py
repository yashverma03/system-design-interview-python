from django.urls import include, path

urlpatterns = [
  path('api/users', include('user.urls')),
]
