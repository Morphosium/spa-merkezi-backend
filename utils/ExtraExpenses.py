from dateutil.parser import parse
from django.db.models import Sum

from api_gider.serializers import EkstraGiderSerializer
from cinarspa_models.models import EkstraGider


def extra_expenses(branch, date_, daily=False):
    date = date_
    if type(date) is str:
        date = parse(date)

    filter = {
        "tarih__month": date.month,
        "tarih__year": date.year,
        "sube__id": branch
    }
    if daily:
        filter["tarih__date"] = date.date

    digerGiderler_ = EkstraGider.objects.filter(**filter).order_by("-id")
    digerGiderler = [EkstraGiderSerializer(gider).data for gider in digerGiderler_]
    return digerGiderler


def extra_expenses_sum(branch, date_, daily=False):
    date = date_
    filter = {
        "tarih__month": date.month,
        "tarih__year": date.year,
        "sube__id": branch
    }
    if daily:
        filter["tarih__day"] = str(date.day)

    if type(date) is str:
        date = parse(date)
    giderToplam = EkstraGider.objects.filter(**filter).aggregate(Sum('tutar'))
    return giderToplam
