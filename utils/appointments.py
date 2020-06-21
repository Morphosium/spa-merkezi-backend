from cinarspa_models.models import Randevu
from api_randevu.serializers import RandevuSerializer
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from utils.SubeIliskileri import iliskiliSubeler


def makeArraySerializations(user: User):
    appointments = []
    modelQuery = ""
    if user.is_superuser:
        modelQuery = Randevu.objects.all()
    elif user.is_staff:
        subeList = iliskiliSubeler(user)
        modelQuery = Randevu.objects.all()
        # TODO: şeye göre filtrele

    for randevuInstance in Randevu.objects.all():
        serializer = RandevuSerializer(randevuInstance)
        appointments.append(serializer.data)
    return appointments
