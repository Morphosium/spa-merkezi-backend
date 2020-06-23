from cinarspa_models.models import MusteriGirisi
from api_gelir.serializers import MusteriGirisiSerializer
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from utils.SubeIliskileri import iliskiliSubeler

def makeArraySerializationsQuery(qAll):
    girisler = []
    for musteriGirisi in qAll:
        serializer = MusteriGirisiSerializer(musteriGirisi)
        girisler.append(serializer.data)
    return girisler

def makeArraySerializationsUserAdministration(user: User):
    appointments = []
    gelenRandevular = ""
    print(user)
    if user.is_superuser:
        gelenRandevular = MusteriGirisi.objects.all()
    elif user.is_staff:
        subeList = iliskiliSubeler(user)
        gelenRandevular = MusteriGirisi.objects.filter(secili_sube__in=subeList)

    for randevuInstance in gelenRandevular:
        serializer = MusteriGirisiSerializer(randevuInstance)
        appointments.append(serializer.data)
    return appointments
