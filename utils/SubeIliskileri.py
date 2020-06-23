
from django.contrib.auth.models import User
from django.http import HttpRequest
from cinarspa_models.models import SubeTemsilcisi

def iliskiliSubeler(user : User) -> list:
    return [temsil.sube for temsil in SubeTemsilcisi.objects.filter(kullanici = user)]

def iliskiVarMi(user: User, subeId = 0, alreadySubeList= None) -> bool:
    if alreadySubeList is not None:
        branchrel = filter(lambda sube: sube.id == subeId, alreadySubeList)
        relationABranch = list(branchrel)
        return relationABranch[0] if len(relationABranch) >= 1 else None
    else:
        temsiller = SubeTemsilcisi.objects.filter(kullanici=user, sube__id=subeId)
        return temsiller[0] if temsiller.count() > 0 else None
