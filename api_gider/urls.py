from rest_framework.urls import url

from api_gider.views import RemoveExpense, AddExpense, ExtraExpensesMonthly

urlpatterns = [
    url(r'^ekstra-giderler/sil', RemoveExpense.as_view()),
    url(r'^ekstra-giderler/ekle', AddExpense.as_view()),
    url(r'^ekstra-giderler', ExtraExpensesMonthly.as_view()),
]

app_name = 'gider_api'