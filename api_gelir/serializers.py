from cinarspa_models.models import MusteriGirisi, MusteriKredi
from rest_framework import serializers

from cinarspa_models.serializers import MusteriSerializer, SubeSerializer
from api_user.serializers import  UserSerializer

class MusteriGirisiSerializer(serializers.ModelSerializer):
    sube_adresi = serializers.CharField(source='secili_sube.sube_ismi')
    calisan = UserSerializer()
    musteri_bilgiler = MusteriSerializer(source="musteri")

    class Meta:
        model = MusteriGirisi
        fields = [
            "calisan",
            "musteri_bilgiler",
            "id",
            "secili_sube",
            "sube_adresi",
            "hizmet_turu",
            "giris_tarih",
            "cikis_tarih",
            "ucret",
            "prim",
            "odeme_yontemi"

        ]


class MusteriKrediSerializer(serializers.ModelSerializer):
    musteri = MusteriSerializer()
    sube = SubeSerializer()
    class Meta:
        model = MusteriKredi
        fields = [
            "sayi",
            "musteri",
            "sube",
            "hizmet_turu",
        ]