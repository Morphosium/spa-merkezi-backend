from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    # Your URLs...
      url(r'^api-token-auth/', obtain_jwt_token),
]