from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.urls import url
from .views import loggedUserInformation, createUser, getBranches
urlpatterns = [
    # Your URLs...
      url(r'^authorize/', obtain_jwt_token),
      url(r'^get-user-info/', loggedUserInformation.as_view()),
      url(r'^create-user', createUser.as_view()),
      url(r'^related-branchs', getBranches.as_view())
]

app_name = 'user_api'