from cinarspa_models.models import Randevu
from api_randevu.serializers import RandevuSerializer
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from utils.SubeIliskileri import iliskiliSubeler


def makeArraySerializations(user: User):
    appointments = []
    gelenRandevular = ""
    print(user)
    if user.is_superuser:
        gelenRandevular = Randevu.objects.all()
    elif user.is_staff:
        subeList = iliskiliSubeler(user)
        gelenRandevular = Randevu.objects.filter(secili_sube__in=subeList)

    for randevuInstance in gelenRandevular:
        serializer = RandevuSerializer(randevuInstance)
        appointments.append(serializer.data)
    return appointments
