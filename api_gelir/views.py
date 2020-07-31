import traceback

from django.db.models import Q
from django.db.models.sql import Query
from django.shortcuts import render
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from api_gelir.serializers import MusteriGirisiSerializer, MusteriKrediSerializer
from cinarspa_models.models import MusteriGirisi, SubeTemsilcisi, Musteri, MusteriKredi
from cinarspa_models.serializers import MusteriSerializer
from utils import SubeIliskileri
from utils.ExtraExpenses import extra_expenses, extra_expenses_sum
from utils.SubeIliskileri import iliskiliSubeler, iliskiVarMi
from utils.arrayUtils import containsInDictionaryKey
from utils.customerUtils import try_fetch
from utils.errorResponse import createErrorResponse
from utils.musteri_girisi import makeArraySerializationsQuery
from utils.pagination import pagination
from dateutil.parser import parse as dateUtilParse
import datetime
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
                customerEntries = MusteriGirisi.objects.order_by("-id").all()
            else:
                customerEntries = MusteriGirisi.objects.filter(secili_sube__id=subeFiltre).order_by("-id")
            paginated = pagination(customerEntries, request.query_params.get("page"), request.query_params.get("size"))
            return Response(makeArraySerializationsQuery(paginated))
        # if not admin but staff
        elif request.user.is_staff:
            if subeFiltre > -1:
                iliskiliSube = iliskiVarMi(request.user, subeFiltre, relations)
                if iliskiliSube is not None:
                    customerEntries = customersQ.filter(secili_sube=iliskiliSube).order_by("-id")
                    paginated = pagination(customerEntries, request.query_params.get("page"),
                                           request.query_params.get("size"))
                    return Response(makeArraySerializationsQuery(paginated))
                else:
                    return createErrorResponse(
                        403,
                        {
                            "message": "You aren't related with ŞUBE(Branch)"
                                       + str(subeFiltre)
                        },
                    )
            else:
                customerEntries = customersQ.filter(secili_sube__in=relations).order_by("-id")
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
        subeFiltre = None
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
                musteriIds = MusteriGirisi.objects.filter(secili_sube__id=subeFiltre).values_list('musteri', flat=True)
                musteriler = Musteri.objects.filter(id__in=musteriIds)
                # sube__id=subeFiltre
                # krediler =

                for musteri in musteriler:
                    rd.append(MusteriSerializer(musteri).data)
                return Response(rd)
            else:
                return createErrorResponse(404, {"message": "Sube is not found"})
        else:
            return createErrorResponse(400, {"message": "Sube id is invalid"})


class musteriKredi(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        load = request.data
        subeid = load.get("sube_id")

        if subeid is not None:
            subeid = int(subeid)
            if iliskiVarMi(request.user, subeid) is not None:
                musteri = try_fetch(load.get("musteri_id"),
                                    load.get("musteri_isim"),
                                    load.get("musteri_soyisim"),
                                    load.get("musteri_email"),
                                    load.get("musteri_tel"), False)
                if musteri is not None:
                    krediler = MusteriKredi.objects.filter(musteri=musteri, sube__id=subeid)
                    ra = []
                    if krediler is not None:
                        for kredi in krediler:
                            ra.append(MusteriKrediSerializer(kredi).data)
                        return Response(ra)
                    else:
                        return Response([])
                else:
                    return Response([])
            else:
                return Response({"message": "Şube yetkisi bulunamadı"}, status=401)
        else:
            return Response({"message": "Girilen gerekli bilgiler geçerli değil"}, status=400)


class yeniMusteriGirisi(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
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
                        if data.get("kredi_ekle") is True or data.get("kredi_tuket") is True:
                            tuketilecek_kredi_turu = data.get("kredi_tuketim_turu")
                            eklenecek_kredi_turu = data.get("kredi_eklenme_turu")

                            eklenecek_kredi, ek_taze = None, None
                            tuketilecek_kredi, tk_taze = None, None

                            if data.get("kredi_ekle") and eklenecek_kredi_turu and \
                                    eklenecek_kredi_turu.isspace() is not True:
                                eklenecek_kredi, ek_taze = MusteriKredi.objects.get_or_create(musteri=musteri,
                                                                                              sube=iliski.sube,
                                                                                              hizmet_turu=eklenecek_kredi_turu)

                            if eklenecek_kredi:
                                # kredi ekleme
                                kredi_eklenecek_sayi = data.get("credit_will_be_added")
                                if kredi_eklenecek_sayi is not None and kredi_eklenecek_sayi > 0:
                                    eklenecek_kredi.sayi += kredi_eklenecek_sayi

                            if data.get("kredi_tuket") and tuketilecek_kredi_turu and \
                                    tuketilecek_kredi_turu.isspace() is not True:
                                if (eklenecek_kredi is not None) and (eklenecek_kredi_turu == tuketilecek_kredi_turu):
                                    tuketilecek_kredi = eklenecek_kredi
                                else:
                                    tuketilecek_kredi, tk_taze = MusteriKredi.objects. \
                                        get_or_create(musteri=musteri,
                                                      sube=iliski.sube, hizmet_turu=tuketilecek_kredi_turu)

                            if tuketilecek_kredi:
                                if tuketilecek_kredi.sayi > 0:
                                    tuketilecek_kredi.sayi -= 1
                                else:
                                    return createErrorResponse(400,
                                                               {"message": "Müşterinin kredi hakkı bulunmamaktadır"})
                            if eklenecek_kredi and \
                                    (tuketilecek_kredi is None or tuketilecek_kredi.id != eklenecek_kredi.id):
                                eklenecek_kredi.save()
                            if tuketilecek_kredi:
                                tuketilecek_kredi.save()

                        musteriKayit = MusteriGirisi(
                            musteri=musteri,
                            hizmet_turu=data.get("hizmet_turu"),
                            secili_sube=iliski.sube,
                            giris_tarih=giris_tarih,
                            cikis_tarih=cikis_tarih,
                            odeme_yontemi=data.get("odeme_yontemi"),
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
                                                                                        values_list("secili_sube",
                                                                                                    flat=True))):
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
                    setattr(kayit, key, upd[key])
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

    def post(self, request: Request):
        try:
            q = request.data
            kayitId = q.get("kayit_id")
            if kayitId is not None and kayitId > -1:
                girisler = MusteriGirisi.objects.filter(id=kayitId)
                if girisler.count() > 0:
                    giris: MusteriGirisi = girisler[0]
                    sube = iliskiVarMi(request.user, giris.secili_sube.id)
                    if request.user.is_superuser or sube is not None:
                        if containsInDictionaryKey(q, [
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


class musteriGirisiSil(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request: Request):
        kayit_id = request.query_params.get("kayit_id")
        if (kayit_id is not None and kayit_id.isnumeric()):
            kayit = MusteriGirisi.objects.filter(id=int(kayit_id))
            if (kayit.count() > 0):
                kayit_: MusteriGirisi = kayit[0]
                temsil = SubeTemsilcisi.objects.filter(kullanici=request.user, sube=kayit_.secili_sube)
                if request.user.is_superuser or temsil.count() > 0:
                    kayit_.delete()
                    return createErrorResponse(200, {"message": "Kayit silindi"})
                else:
                    return createErrorResponse(403, {"message": "İzin bulunamadı"})
            else:
                return createErrorResponse(401, {"message": "Kayit bulunamadı"})
        else:
            return createErrorResponse(401, {"message": "Kayit bulunamadı"})


def _report(request, daily=False):
    subeid_ = request.query_params.get("sube")
    if subeid_ and subeid_.isnumeric():
        subeid = int(subeid_)
        iliskiler = SubeTemsilcisi.objects.filter(sube__id=subeid, kullanici=request.user)

        iliski = iliskiler[0] if iliskiler.count() > 0 else None
        if request.user.is_superuser or iliski is not None:
            aylik_toplam_gelir = 0
            aylik_toplam_prim = 0
            bugun = ""
            if "refdate" in request.query_params.keys():
                bugun = dateUtilParse(request.query_params["refdate"])
            else:
                bugun = datetime.date.today()
            gidertoplam = extra_expenses_sum(subeid, bugun, daily)["tutar__sum"]
            if gidertoplam is None:
                gidertoplam = 0
            calisan_primler = None
            if request.user.is_superuser or iliski.ustduzey_hak is True:
                calisan_primler = {}

            filter = {
                "secili_sube__id": subeid,
                "giris_tarih__month": bugun.month,
                "giris_tarih__year": bugun.year
            }
            if daily is True:
                filter["giris_tarih__day"] = str(bugun.day)

            aylik_kayitlar = MusteriGirisi.objects.filter(
                **filter)

            for kayit in aylik_kayitlar:
                aylik_toplam_prim += kayit.prim
                aylik_toplam_gelir += kayit.ucret
                if request.user.is_superuser or iliski.ustduzey_hak is True:
                    if kayit.calisan.id in calisan_primler.keys():
                        calisan_primler[kayit.calisan.id] += kayit.prim
                    else:
                        calisan_primler[kayit.calisan.id] = kayit.prim

            return Response({
                "summary": {
                    "income": aylik_toplam_gelir,
                    "bonus_grand": aylik_toplam_prim,
                    "extra_expenses": gidertoplam,
                    "grand_expenses": aylik_toplam_prim + gidertoplam
                },
                "bonuses": calisan_primler,

            })
        else:
            return createErrorResponse(403, {"message": "Not authorized for branch"})
    else:
        return createErrorResponse(400, {"message": "Branch is not provided"})


class monthlyReport(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request: Request):
        return _report(request)


class dailyReport(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return _report(request, True)
