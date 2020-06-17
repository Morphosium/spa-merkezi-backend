from django.db import models
from cinarspa_models.submodels.sube import Sube

# Create your models here.
class Randevu(models.Model):
    secili_sube = models.ForeignKey("generalmodels.Sube", on_delete=models.CASCADE)
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



