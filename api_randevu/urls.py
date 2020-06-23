from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.urls import url
from .views import createAppointment, fetchAuthorizedAppointments

urlpatterns = [
    # Your URLs...
      url(r'^appointment/create', createAppointment.as_view()),
      url(r'^appointment/fetch', fetchAuthorizedAppointments.as_view()),

]

app_name = 'randevu_api'