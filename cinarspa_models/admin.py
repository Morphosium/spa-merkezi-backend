from django.contrib import admin
from .models import Sube, SubeTemsilcisi, Randevu, MusteriGirisi, Musteri, EkstraGider

# Register your models here.
admin.site.register(Sube)
admin.site.register(SubeTemsilcisi)
admin.site.register(Randevu)
admin.site.register(MusteriGirisi)
admin.site.register(Musteri)
admin.site.register(EkstraGider)