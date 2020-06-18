from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from utils.arrayUtils import containsInDictionaryKey
from utils.errorResponse import createErrorResponse
from cinarspa_models.models import Sube, SubeTemsilcisi, Randevu
from datetime import datetime
import traceback
import sys
from dateutil.parser import parse as dateUtilParse
# Create your views here.




class createAppointment(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data: dict = request.data
            if containsInDictionaryKey(
                data, ["isimSoyisim", "hizmetTipi", "subeId", "tarih"]
            ):
                # create RANDEVU(Appointment) instance - RANDEVU örneği yaratma
                # find SUBE (Branch) - şube arama
                subeler = Sube.objects.filter(id=data.get("subeId"))
                if subeler.count() > 0:
                    sube = subeler[0]
                    tarih = dateUtilParse(data.get("tarih"))
                    #tarih = datetime.strptime(data.get("tarih"),"%Y-%m-%dT%H:%M:%S.%Z")
                    randevu = Randevu(secili_sube = sube,
                            hizmet_turu  = data.get("hizmetTipi"),
                            tarih = tarih,
                    )
                    randevu.save()
                    return createErrorResponse(
                        200, {"message": """Appointment created successfully"""}
                    )
                else:
                    return createErrorResponse(
                        400, {"message": """ Branch not found """}
                    )  #

            else:
                return createErrorResponse(
                    400,
                    {
                        "message": """1 field or more than 1 fields are missing. Needed "isimSoyisim" (first - last names),"hizmetTipi" (service type),"subeId" (branch identify),"tarih" (date with hours) fields """
                    },
                )  #

        except Exception as exception:
            traceback.print_exc()
            return createErrorResponse(500,{"error": str(exception.__class__)})
