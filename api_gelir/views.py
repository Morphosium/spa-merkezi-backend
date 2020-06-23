import traceback

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated, AllowAny

from api_gelir.serializers import MusteriGirisiSerializer
from cinarspa_models.models import MusteriGirisi
from utils.SubeIliskileri import iliskiliSubeler, iliskiVarMi
from utils.arrayUtils import containsInDictionaryKey
from utils.errorResponse import createErrorResponse
from utils.musteri_girisi import makeArraySerializationsQuery
from dateutil.parser import parse as dateUtilParse
import re


# Create your views here.


class musteriGirisleri(APIView):
    permission_classes = [IsAuthenticated, ]
    """Müşteri girişlerini getirmek için kullanılır
        query parametreleri
        - sadece-cikmayanlar = 1 ise çıkış tarihi null olanlar döner
        - sube = int şeklinde şube id girilir. Eğer yetki yoksa 403-YASSAH kodu döner
    """

    def get(self, request: Request):
        """@sadeceCikmayanlar çıkış tarihi eklenmemiş kayıtları gösterir
           @subeFiltre"""

        sadeceCikmayanlar = False
        subeFiltre = -1

        if request.query_params.get("sadece-cikmayanlar") == "1":
            sadeceCikmayanlar = True

        subeId: str = request.query_params.get("sube")
        if (
                subeId != "" and
                subeId is not None and
                re.match("^([0-9].*)$", subeId) is not None):
            subeFiltre = int(subeId)

        customersQ = MusteriGirisi.objects
        if (sadeceCikmayanlar):
            customersQ = customersQ.filter(cikis_tarih__isnull=True)
        relations = iliskiliSubeler(request.user)
        if request.user.is_superuser:
            customerEntries = customersQ.all()
            return Response(makeArraySerializationsQuery(customerEntries))
        elif request.user.is_staff:
            if subeFiltre > -1:
                iliskiliSube = iliskiVarMi(request.user, subeFiltre, relations)
                if iliskiliSube is not None:
                    customerEntries = customersQ.filter(secili_sube=iliskiliSube).all()
                    return Response(makeArraySerializationsQuery(customerEntries))
                else:
                    return createErrorResponse(403,
                                               {"message": "You aren't related with ŞUBE(Branch)" + str(subeFiltre)})
            else:
                customerEntries = customersQ.filter(secili_sube__in=relations)
                return Response(makeArraySerializationsQuery(customerEntries.all()))


class yeniMusteriGirisi(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            data: dict = request.data
            if containsInDictionaryKey(
                    data, ["isim", "soyisim", "hizmetTipi", "girisTarihi", "sube"]
                    # optional fields = ucret, cikisTarihi
            ):
                cikis_tarih = None
                giris_tarih = dateUtilParse(data.get("girisTarihi"))
                ucret = data.get("ucret")

                if (data.get("cikisTarihi") is not None):
                    cikis_tarih = dateUtilParse(data.get("cikisTarihi"))
                iliski = iliskiVarMi(request.user, data.get("sube"))
                if (iliski is not None):
                    musteriKayit = MusteriGirisi(
                        musteri_isim=data.get("isim"),
                        musteri_soyisim=data.get("soyisim"),
                        hizmet_turu=data.get("hizmetTipi"),
                        secili_sube=iliski.sube,
                        giris_tarih=giris_tarih,
                        cikis_tarih=cikis_tarih,
                        ucret=ucret if ucret is not None else 0,
                        calisan=request.user
                    )
                    musteriKayit.save()
                    return createErrorResponse(200, MusteriGirisiSerializer(musteriKayit).data)
                else:
                    return createErrorResponse(403, {"message":
                                                         "You aren't related with ŞUBE(Branch)" + str(
                                                             request.data.get("sube"))
                                                     })

            else:
                return createErrorResponse(
                    400,
                    {
                        "message": """1 field or more than 1 fields are missing. 
                                    Needed "isim", "soyisim" (first - last names),"hizmetTipi" (service type),
                                    "subeId" (branch identify),"tarih" (date with hours) fields """
                    },
                )  #

        except Exception as exception:
            traceback.print_exc()
            return createErrorResponse(500, {"error": str(exception.__class__)})
