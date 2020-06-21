
from django.contrib.auth.models import User
from django.http import HttpRequest
from cinarspa_models.models import SubeTemsilcisi

def iliskiliSubeler(user : User) -> SubeTemsilcisi:
    return [temsil.sube for temsil in SubeTemsilcisi.objects.filter(kullanici = user)]
    # if (subeTemsilcileri.count() > 0):
    #     temsilciYetkileri = []
    #     for temsil in subeTemsilcileri.objects():
    #         temsilciYetkileri.append(temsil)
    #     return temsilciYetkileri
    # else:
    #     return None
