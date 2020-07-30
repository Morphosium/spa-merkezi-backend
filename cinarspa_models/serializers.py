from rest_framework.serializers import ModelSerializer

from cinarspa_models.models import Musteri, Sube


class MusteriSerializer(ModelSerializer):
    class Meta:
        model = Musteri
        fields = [
            "id", "isim", "soyisim", "tel", "email"
        ]


class SubeSerializer(ModelSerializer):
    class Meta:
        model = Sube
        fields = [
            "adres",
            "sube_ismi",
            "id"
        ]