
from django.contrib.auth.models import User
from django.http import HttpRequest
from cinarspa_models.models import SubeTemsilcisi

def iliskiliSube(request : HttpRequest) -> SubeTemsilcisi:
    subeTemsilcileri = SubeTemsilcisi.objects.filter(kullanici = request.user)
    if (subeTemsilcileri.count() > 0):
        temsilciYetkileri = []
        for temsil in subeTemsilcileri.objects():
            temsilciYetkileri.append(temsil)
        return temsilciYetkileri
    else:
        return None
