from cinarspa_models.models import Randevu
from rest_framework import serializers

from cinarspa_models.serializers import MusteriSerializer


class RandevuSerializer(serializers.ModelSerializer):
    subeId = serializers.CharField(source='secili_sube.id')
    subeAdresi = serializers.CharField(source='secili_sube.sube_ismi')

    musteri = MusteriSerializer()
    class Meta:
        model = Randevu
        fields = [
            'musteri',
            'hizmet_turu',
            'tarih',
            'subeId',
            'subeAdresi']
