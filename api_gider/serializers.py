from cinarspa_models.models import EkstraGider
from rest_framework import serializers

from cinarspa_models.serializers import MusteriSerializer, SubeSerializer
from api_user.serializers import UserSerializer


class EkstraGiderSerializer(serializers.ModelSerializer):
    # sube_adresi = serializers.CharField(source='secili_sube.sube_ismi')
    # calisan = UserSerializer()
    # musteri_bilgiler = MusteriSerializer(source="musteri")
    sube = SubeSerializer()
    class Meta:
        model = EkstraGider
        fields = [
            "baslik", "detay", "tur", "tarih", "tutar", "sube", "id"
        ]
