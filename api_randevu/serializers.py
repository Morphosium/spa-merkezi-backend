from cinarspa_models.models import Randevu
from rest_framework import serializers


class RandevuSerializer(serializers.ModelSerializer):
    subeId = serializers.CharField(source='secili_sube.id')
    subeAdresi = serializers.CharField(source='secili_sube.sube_ismi')

    class Meta:
        model = Randevu
        fields = [
            'musteri_isim',
            'musteri_soyisim',
            'musteri_email',
            'musteri_tel',
            'hizmet_turu',
            'tarih',
            'subeId',
            'subeAdresi']
