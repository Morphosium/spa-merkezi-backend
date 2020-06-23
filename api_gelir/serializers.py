from cinarspa_models.models import MusteriGirisi
from rest_framework import serializers


class MusteriGirisiSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusteriGirisi
        fields = ['id', 'secili_sube', 'hizmet_turu', 'giris_tarih', 'cikis_tarih']
