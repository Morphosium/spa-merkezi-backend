from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.urls import url
from .views import musteriGirisleri, yeniMusteriGirisi, musteriCikisi, musteriler, girisiDuzenle

urlpatterns = [
    # Your URLs...
      url(r'^customer-entries/create', yeniMusteriGirisi.as_view()),
      url(r'^customer-entries/cikis-ver', musteriCikisi.as_view()),
      url(r'^customer-entries/musteriler', musteriler.as_view()),
      url(r'^customer-entries/update', girisiDuzenle.as_view()),
      url(r'^customer-entries/', musteriGirisleri.as_view()),


]

app_name = 'gelir_api'