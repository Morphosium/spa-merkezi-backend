from cinarspa_models.models import Randevu
from rest_framework import serializers
class RandevuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Randevu
        fields = ['secili_sube', 'hizmet_turu', 'tarih']