import traceback

from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny

from utils.errorResponse import createErrorResponse
from .serializers import UserSerializer
from utils.SubeIliskileri import iliskiVarMi, iliskiliSubeler, iliskiliKullanicilar
from cinarspa_models.models import SubeTemsilcisi


# Create your views here.


class loggedUserInformation(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if (request.user is not None):
            userSerializer = UserSerializer(request.user)
            return Response(userSerializer.data)


class createUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            subeId = request.data["subeId"] if "subeId" in request.data else -1
            arananSube = None
            if subeId == -1:
                return createErrorResponse(404, {"message": "Branch not found"})
            else:
                arananSube = iliskiVarMi(request.user, subeId)
                if arananSube is None:
                    return createErrorResponse(404, {"message": "Branch not found"})

            if request.user.is_staff:
                kul_id = request.user.id
                stFilter = SubeTemsilcisi.objects.filter(sube__id=subeId, kullanici__id=kul_id)[0]
            elif request.user.is_superuser:
                stFilter = SubeTemsilcisi.objects.filter(sube__id=subeId)[0]

            serialized = UserSerializer(data=request.data)

            # subeAuthorized = iliskiliSubeler(request.user)
            if subeId > -1 and iliskiVarMi(request.user, subeId):
                if serialized.is_valid():
                    createdUser = User.objects.create_user(
                        email=request.data['email'],
                        username=request.data['username'],
                        password=request.data['password'],
                        is_staff=True
                    )
                    createdUser.save()
                    yeniSubeIliskisi = SubeTemsilcisi(
                        sube=stFilter.sube,
                        kullanici=createdUser
                    )
                    yeniSubeIliskisi.save()
                    return Response(serialized.data, status=status.HTTP_201_CREATED)
                else:
                    return createErrorResponse(404, serialized.errors)
            else:
                return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exception:
            traceback.print_exc()
            return createErrorResponse(500, {"error": str(exception.__class__)})


class getBranches(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subeler = iliskiliSubeler(request.user)
        ls = [{"id": sube.id, "name": sube.sube_ismi, "address": sube.adres}
              for sube in subeler]

        return Response(ls)


class getStaffsInBranch(APIView):
    permission_classes = [IsAuthenticated]

    def __combineTemsil(self, temsil : SubeTemsilcisi):
        return {**UserSerializer(temsil.kullanici).data, **{"sube_ismi": temsil.sube.sube_ismi, "sube_id": temsil.sube.id}}

    def get(self, request, sube=-1):
        if (sube > -1):
            if request.user.is_superuser or iliskiVarMi(request.user, sube) is not None:
                iliskiler = SubeTemsilcisi.objects.filter(sube__id=sube)
                calisanlar_parsed = [self.__combineTemsil(iliski) for iliski in iliskiler]
                return createErrorResponse(202, calisanlar_parsed)
            else:
                return createErrorResponse(403, {"message": "Unauthorized branch"})
        else:

            if request.user.is_superuser:
                iliskiler = SubeTemsilcisi.objects.filter()
                calisanlar_parsed = [self.__combineTemsil(iliski)
                                     for iliski in iliskiler]
                return createErrorResponse(202, calisanlar_parsed)
            else:
                subeler = iliskiliSubeler(request.user)
                iliskiler = SubeTemsilcisi.objects.filter(sube__in=subeler)
                calisanlar_parsed = [self.__combineTemsil(iliski) for iliski in iliskiler]
                return createErrorResponse(202, calisanlar_parsed)
