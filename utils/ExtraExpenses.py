from dateutil.parser import parse

from cinarspa_models.models import EkstraGider


def extra_expenses(branch, date_):
    date = date_
    if type(date) is str:
        date = parse(date)
    digerGiderler = EkstraGider.objects.filter(tarih__month=date.month, tarih__year=date.year, sube__id=branch)
    return digerGiderler