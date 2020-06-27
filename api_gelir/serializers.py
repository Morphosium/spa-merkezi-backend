from cinarspa_models.models import MusteriGirisi
from rest_framework import serializers


class MusteriGirisiSerializer(serializers.ModelSerializer):
    sube_adresi = serializers.CharField(source='secili_sube.sube_ismi')

    class Meta:
        model = MusteriGirisi
        fields = [
            "id",
            "musteri_isim",
            "musteri_soyisim",
            "musteri_email",
            "musteri_tel",
            "secili_sube",
            "sube_adresi",
            "hizmet_turu",
            "giris_tarih",
            "cikis_tarih",
            "ucret"
        ]
