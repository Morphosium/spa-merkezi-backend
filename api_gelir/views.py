import traceback

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from api_gelir.serializers import MusteriGirisiSerializer
from cinarspa_models.models import MusteriGirisi, SubeTemsilcisi, Musteri
from cinarspa_models.serializers import MusteriSerializer
from utils import SubeIliskileri
from utils.SubeIliskileri import iliskiliSubeler, iliskiVarMi
from utils.arrayUtils import containsInDictionaryKey
from utils.customerUtils import try_fetch
from utils.errorResponse import createErrorResponse
from utils.musteri_girisi import makeArraySerializationsQuery
from dateutil.parser import parse as dateUtilParse
import re


# Create your views here.


class musteriGirisleri(APIView):
    permission_classes = [
        IsAuthenticated,
    ]
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

        subeId: str = request.query_params.get("sube-id")
        if (
            subeId != ""
            and subeId is not None
            and re.match("^([0-9].*)$", subeId) is not None
        ):
            subeFiltre = int(subeId)

        customersQ = MusteriGirisi.objects
        if sadeceCikmayanlar:
            customersQ = customersQ.filter(cikis_tarih__isnull=True)
        relations = iliskiliSubeler(request.user)
        # admin control
        if request.user.is_superuser:
            customerEntries = None
            if subeFiltre == -1:
                customerEntries = MusteriGirisi.objects.all()
            else:
                customerEntries = MusteriGirisi.objects.filter(secili_sube__id=subeFiltre)
            return Response(makeArraySerializationsQuery(customerEntries))
        # if not admin but staff
        elif request.user.is_staff:
            if subeFiltre > -1:
                iliskiliSube = iliskiVarMi(request.user, subeFiltre, relations)
                if iliskiliSube is not None:
                    customerEntries = customersQ.filter(secili_sube=iliskiliSube).all()
                    return Response(makeArraySerializationsQuery(customerEntries))
                else:
                    return createErrorResponse(
                        403,
                        {
                            "message": "You aren't related with ŞUBE(Branch)"
                            + str(subeFiltre)
                        },
                    )
            else:
                customerEntries = customersQ.filter(secili_sube__in=relations)
                return Response(makeArraySerializationsQuery(customerEntries.all()))

class musteriler(APIView):
    permission_classes = [
        IsAuthenticated,
    ]
    """Müşteri girişlerini getirmek için kullanılır
        query parametreleri
        - sadece-cikmayanlar = 1 ise çıkış tarihi null olanlar döner
        - sube = int şeklinde şube id girilir. Eğer yetki yoksa 403-YASSAH kodu döner
    """

    def get(self, request: Request):
        subeFiltre=None
        subeId: str = request.query_params.get("sube-id")
        if (
            subeId != ""
            and subeId is not None
            and re.match("^([0-9].*)$", subeId) is not None
        ):
            subeFiltre = int(subeId)
            temsil = iliskiVarMi(request.user, subeFiltre)
            if request.user.is_superuser or temsil is not None:
                rd = []
                musteriler = Musteri.objects.filter(id__in=MusteriGirisi.objects.filter(secili_sube__id=subeFiltre).values_list('musteri', flat=True))
                for musteri in musteriler:
                    rd.append(MusteriSerializer(musteri).data)
                return Response(rd)
            else:
                return createErrorResponse(404, {"message": "Sube is not found"})
        else:
            return createErrorResponse(400, {"message": "Sube id is invalid"})




class yeniMusteriGirisi(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        #TODO: İlgelenen çalışan ekleme
        try:
            data: dict = request.data
            if containsInDictionaryKey(
                data,
                [
                    "musteri_isim",
                    "musteri_soyisim",
                    "musteri_email",
                    "musteri_tel",
                    "hizmet_turu",
                    "giris_tarih",
                    "secili_sube",
                    "calisan"
                ]
                # optional fields = ucret, cikisTarihi
            ) or containsInDictionaryKey(
                data,
                [
                    "musteri_id",
                    "hizmet_turu",
                    "giris_tarih",
                    "secili_sube",
                    "calisan"
                ]
                # optional fields = ucret, cikisTarihi
            ):
                ilgili_calisan_id = data.get("calisan")
                bulunanCalisan = SubeTemsilcisi.objects.filter(
                    kullanici__id=int(ilgili_calisan_id),
                    sube__id=int(data.get("secili_sube"))
                    )

                email, tel = "", "";
                if ("musteri_email" in data.keys()):
                    email = data.get("musteri_email")

                if ("musteri_tel" in data.keys()):
                    tel = data.get("musteri_tel")

                musteri = try_fetch(data.get("musteri_id"), data.get("musteri_isim"),
                                             data.get("musteri_soyisim"), email, tel)

                if bulunanCalisan.count() > -1:
                    cikis_tarih = None
                    giris_tarih = dateUtilParse(data.get("giris_tarih"))

                    email = ""
                    tel = ""
                    if "musteri_email" in data:
                        email = data.get("musteri_email")

                    if "musteri_tel" in data:
                        tel = data.get("musteri_tel")

                    ucret = data.get("ucret")
                    prim = data.get("prim")
                    calisan = None
                    calisanId = data.get("calisan")
                    if calisanId is not None and calisanId.isnumeric():
                        calisan = User.objects.filter(id=int(calisanId))

                    if (calisan is None):
                        calisan = request.user

                    if data.get("cikis_tarih") is not None:
                        cikis_tarih = dateUtilParse(data.get("cikis_tarih"))

                    iliski = iliskiVarMi(request.user, data.get("secili_sube"))

                    calisanIliski = SubeTemsilcisi.objects.filter(kullanici=calisan[0], sube=data.get("secili_sube"))[0]

                    if request.user.is_superuser or iliski is not None:
                        musteriKayit = MusteriGirisi(
                            musteri=musteri,
                            hizmet_turu=data.get("hizmet_turu"),
                            secili_sube=iliski.sube,
                            giris_tarih=giris_tarih,
                            cikis_tarih=cikis_tarih,
                            ucret=ucret if ucret is not None else 0,
                            calisan=calisanIliski.kullanici,
                            prim=prim
                        )
                        musteriKayit.save()
                        return createErrorResponse(
                            200, MusteriGirisiSerializer(musteriKayit).data
                        )
                    else:
                        return createErrorResponse(
                            403,
                            {
                                "message": "You aren't related with ŞUBE(Branch)"
                                           + str(request.data.get("sube"))
                            },
                        )
                else:
                    createErrorResponse(404, {"message": "Corresponding User in branch not found"})
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

class girisiDuzenle(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):

        try:
            upd = {}
            if "id" in request.data.keys() and \
                   (request.user.is_superuser or SubeTemsilcisi.objects.filter(kullanici=request.user,
                                                 sube__id__in=MusteriGirisi.objects.
                                                         filter(id=request.data["id"]).
                                                        values_list("secili_sube", flat=True))):
                data = request.data

                if data.get("cikis_tarih") is not None or data.get("cikis_tarih") != "":
                    upd["cikis_tarih"] = dateUtilParse(data.get("cikis_tarih"))

                if data.get("giris_tarih") is not None or data.get("giris_tarih") != "":
                    upd["giris_tarih"] = dateUtilParse(data.get("giris_tarih"))

                if data.get("hizmet_turu") is not None:
                    upd["hizmet_turu"] = data.get("hizmet_turu")

                if data.get("ucret") is not None:
                    upd["ucret"] = data.get("ucret")

                if data.get("prim") is not None:
                    upd["prim"] = data.get("prim")

                if data.get("calisan") is not None:
                    upd["calisan"] = User.objects.filter(id=int(data.get("calisan")))[0]

                recordId = int(request.data["id"])
                kayit = MusteriGirisi.objects.filter(id=recordId).all()[0]
                for key in upd.keys():
                    setattr(kayit,key, upd[key])
                kayit.save()
                return Response({"message": "Record updated"})


            else:
                return createErrorResponse(404, {"message": "Not found"})

        except Exception as exception:
            traceback.print_exc()
            return createErrorResponse(500, {"error": str(exception.__class__)})


class musteriCikisi(APIView):
    permission_classes = [
        IsAuthenticated,
    ]
    def post(self, request : Request):
        try:
            q = request.data
            kayitId = q.get("kayit_id")
            if kayitId is not None and kayitId > -1:
                girisler = MusteriGirisi.objects.filter(id=kayitId)
                if girisler.count() > 0:
                    giris: MusteriGirisi = girisler[0]
                    sube = iliskiVarMi(request.user, giris.secili_sube.id)
                    if request.user.is_superuser or sube is not None:
                        if containsInDictionaryKey(q,[
                            "cikis_tarih", "ucret"
                        ]):
                            cikis_tarih = dateUtilParse(q.get("cikis_tarih"))
                            giris.cikis_tarih = cikis_tarih
                            giris.ucret = q.get("ucret")
                            giris.save()
                            return createErrorResponse(200, {"message": "Record updated"})
                    else:
                        return createErrorResponse(403, {"message": "Unauthorized for this branch"})
                else:
                    return createErrorResponse(404, {"message": "Record not found"})
            else:
                return createErrorResponse(400, {"message": "Record not provided correctly"})

        except Exception as exception:
            traceback.print_exc()
            return createErrorResponse(500, {"error": str(exception.__class__)})