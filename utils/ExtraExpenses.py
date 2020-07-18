from dateutil.parser import parse
from django.db.models import Sum

from api_gider.serializers import EkstraGiderSerializer
from cinarspa_models.models import EkstraGider


def extra_expenses(branch, date_):
    date = date_
    if type(date) is str:
        date = parse(date)
    digerGiderler_ = EkstraGider.objects.filter(tarih__month=date.month,
                                                tarih__year=date.year, sube__id=branch).order_by("-id")
    digerGiderler = [EkstraGiderSerializer(gider).data for gider in digerGiderler_]
    return digerGiderler

def extra_expenses_sum(branch, date_):
    date = date_
    if type(date) is str:
        date = parse(date)
    giderToplam = EkstraGider.objects.filter(tarih__month=date.month,
                                            tarih__year=date.year,
                                             sube__id=branch).aggregate(Sum('tutar'))
    return giderToplam
