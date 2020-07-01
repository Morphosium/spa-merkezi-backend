from cinarspa_models.models import MusteriGirisi
from rest_framework import serializers

from cinarspa_models.serializers import MusteriSerializer


class MusteriGirisiSerializer(serializers.ModelSerializer):
    sube_adresi = serializers.CharField(source='secili_sube.sube_ismi')

    musteri_bilgiler = MusteriSerializer(source="musteri")

    class Meta:
        model = MusteriGirisi
        fields = [
            "musteri_bilgiler",
            "id",
            "secili_sube",
            "sube_adresi",
            "hizmet_turu",
            "giris_tarih",
            "cikis_tarih",
            "ucret",

        ]
