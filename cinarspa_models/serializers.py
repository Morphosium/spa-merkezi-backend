from rest_framework.serializers import ModelSerializer

from cinarspa_models.models import Musteri


class MusteriSerializer(ModelSerializer):
    class Meta:
        model = Musteri
        fields = [
            "id", "isim", "soyisim", "tel", "email"
        ]
