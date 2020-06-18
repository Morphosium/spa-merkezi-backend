from django.db import models
from django.contrib.auth.models import Group, User
from django.conf import settings


class Sube(models.Model):
    adres = models.CharField(max_length = 300)
    sube_ismi = models.CharField(max_length = 100)
    def __str__(self):
        return str(self.sube_ismi).capitalize() + " şubesi"
    class Meta:
        verbose_name = "Şube"
        verbose_name_plural = "Şubeler"

class SubeTemsilcisi(models.Model):
    sube = models.ForeignKey(Sube, on_delete=models.CASCADE)
    kullanici = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    def __str__(self):
        return self.sube.sube_ismi + " => " + self.kullanici.username
    class Meta:
        verbose_name = "Şube temsilcisi"
        verbose_name_plural = "Şube temsilcileri"


# Create your models here.
class Randevu(models.Model):
    secili_sube = models.ForeignKey("cinarspa_models.models.Sube", on_delete=models.CASCADE)
    hizmet_turu = models.CharField(max_length=30)
    tarih = models.DateField()
    def __str__(self):
        return (
            self.secili_sube.sube_ismi
            + " şubesinde "
            + str(self.tarih)
            + " tarihindeki randevu"
        )

    class Meta:
        verbose_name_plural = "Randevular"



