from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated, AllowAny

from utils.SubeIliskileri import iliskiVarMi, iliskiliSubeler
from utils.arrayUtils import containsInDictionaryKey
from utils.errorResponse import createErrorResponse
from utils.appointments import makeArraySerializations
from cinarspa_models.models import Sube, SubeTemsilcisi, Randevu
from datetime import datetime
from .serializers import RandevuSerializer
import traceback
from utils.customerUtils import try_fetch as try_fetch_customer
import sys
from dateutil.parser import parse as dateUtilParse


# Create your views here.

class fetchAuthorizedAppointments(APIView):
    permission_classes = [IsAuthenticated]

    def __convertAppointments(self,gelenRandevular):
        appointments = []
        for randevuInstance in gelenRandevular:
            serializer = RandevuSerializer(randevuInstance)
            appointments.append(serializer.data)
        return appointments

    def get(self, request : Request):
        try:
            subeId: str = request.query_params.get("sube-id")
            if request.user.is_superuser:
                if subeId is not None and subeId.isnumeric():
                    query = Randevu.objects.filter(secili_sube__id=int(subeId))
                    return Response(self.__convertAppointments(query.all()))
                else:
                    return Response(self.__convertAppointments(Randevu.objects.all()))

            else:
                query = Randevu.objects
                if subeId is not None and subeId.isnumeric():
                    temsil = iliskiVarMi(request.user, int(subeId))
                    if temsil is not None:
                        query = query.filter(secili_sube=temsil.sube)
                        return Response(self.__convertAppointments(query.all()))
                    else:
                        return createErrorResponse(403, {"message": "You aren't authenticated with this branch"})
                else:
                    iliskiliBranchler = iliskiliSubeler(request.user)
                    query = Randevu.objects.filter(secili_sube__in=iliskiliBranchler)
                    return Response(self.__convertAppointments(query.all()))



        except Exception as exception:
            traceback.print_exc()
            return createErrorResponse(500, {"error": str(exception.__class__)})


class createAppointment(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data: dict = request.data
            if containsInDictionaryKey(data, ["musteri_isim", "musteri_soyisim","musteri_email","musteri_tel", "hizmetTipi", "subeId", "randevuTarih"]) or \
                    containsInDictionaryKey(data, ["musteri_id", "hizmetTipi", "subeId", "randevuTarih"]):
                # create RANDEVU(Appointment) instance - RANDEVU örneği yaratma
                # find SUBE (Branch) - şube arama


                subeler = Sube.objects.filter(id=data.get("subeId"))
                email, tel = "", "";
                if ("musteri_email" in data.keys()):
                    email = data.get("musteri_email")

                if ("musteri_tel" in data.keys()):
                    tel = data.get("musteri_tel")

                musteri = try_fetch_customer(data.get("musteri_id"), data.get("musteri_isim"),
                                             data.get("musteri_soyisim"),email,tel)

                if subeler.count() > 0:
                    sube = subeler[0]
                    tarih = dateUtilParse(data.get("randevuTarih"))
                    # tarih = datetime.strptime(data.get("tarih"),"%Y-%m-%dT%H:%M:%S.%Z")
                    
                    randevu = Randevu(
                        secili_sube=sube,
                        hizmet_turu=data.get("hizmetTipi"),
                        tarih=tarih,
                        musteri=musteri
                    )
                    randevu.save()
                    return createErrorResponse(
                        200, {"message": """Appointment created successfully"""}
                    )
                else:
                    return createErrorResponse(
                        400, {"message": """Branch not found"""}
                    )  #

            else:
                return createErrorResponse(
                    400,
                    {
                        "message": """1 field or more than 1 fields are missing. Needed "isim", "soyisim" (first - last names),"hizmetTipi" (service type),"subeId" (branch identify),"tarih" (date with hours) fields """
                    },
                )  #

        except Exception as exception:
            traceback.print_exc()
            return createErrorResponse(500, {"error": str(exception.__class__)})


class deleteAppointment(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, randevuId):
        if randevuId is None:
            return createErrorResponse(400, {"message": "randevu Id not provided"})
        else:
            randevular = Randevu.objects.filter(id=randevuId)
            randevu = randevular[0] if randevular.count() > 0 else None
            if randevu is not None:
                iliski = iliskiVarMi(request.user, randevu.secili_sube.id)
                if iliski is not None or request.user.is_superuser:
                    randevu.delete()
                    return Response({"message": "Appointment deleted"}, 200)
                else:
                    return Response({"message": "You are unauthorized for this branch"}, 403)
            else:
                return Response({"message": "Randevu not found"}, 404)
