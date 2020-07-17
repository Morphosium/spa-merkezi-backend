from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from dateutil.parser import parse

from api_gider.serializers import EkstraGiderSerializer
from cinarspa_models.models import EkstraGider, Sube
from utils.ExtraExpenses import extra_expenses
from utils.SubeIliskileri import iliskiVarMi
from utils.errorResponse import createErrorResponse
from utils.pagination import pagination


def _generic_control(request, subePreprovide=None) -> (bool, Response):
    """Controls is branch provided and is user any privaliges
    Return 1: when controlling if has a issue, return false. Else then, it is true
    Return 2: If has issue, response will be returned. But there is no issue, nothing returned"""
    sube_ = ""
    if subePreprovide is None:
        sube_: str = request.query_params["sube_id"]
    else:
        sube_ = subePreprovide
    if type(sube_) is int or sube_.isnumeric():
        sube = int(sube_)
        flag = False
        if (request.user.is_superuser):
            flag = True
        else:
            iliski = iliskiVarMi(request.user, sube)
            if iliski is not None:
                flag = True
        if flag:
            return True, None
            return False, createErrorResponse(200, paginated_expenses)
        else:
            return False, createErrorResponse(404, {"message": "Branch not found"})
    else:
        return False, createErrorResponse(400, {"message": "Branch is missing"})


class ExtraExpensesMonthly(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        flag, errorResponse = _generic_control(request)
        if flag:
            date_ = request.query_params["date"]
            sube = int(request.query_params["sube_id"])
            expenses = extra_expenses(sube, date_)
            paginated_expenses = pagination(expenses, request.query_params.get("page"),
                                            request.query_params.get("size"))
            return createErrorResponse(200, paginated_expenses)
        else:
            return errorResponse

class AddExpense(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        flag, error_response = _generic_control(request)
        if flag:
            copied = request.data.copy()
            sube_id = copied["sube"]

            sube = Sube.objects.filter(id=sube_id)[0]
            copied["sube"] = {"id": sube_id, "adres": "asdasd", "sube_ismi": "sasdas"}
            parsedThing = EkstraGiderSerializer(data=copied)
            if parsedThing.is_valid():
                copied["sube"] = sube
                yeniGider = EkstraGider(**copied)
                yeniGider.save()
                return createErrorResponse(201, {"message": "Expense created successfully",
                                                 "object": EkstraGiderSerializer(yeniGider).data}
                                           )
            else:
                return createErrorResponse(400, {"errors": parsedThing.errors, "message": "Required fields are missing"})
        else:
            return error_response

class RemoveExpense(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.query_params["gider_id"] is not None and request.query_params["gider_id"].isnumeric():
            gider_id = int(request.query_params["gider_id"])
            giderler = EkstraGider.objects.filter(id=gider_id)
            if giderler.count() > 0:
                gider  : EkstraGider = giderler[0]
                giderSube = gider.sube.id
                flag, err_response = _generic_control(request, giderSube)
                if flag:
                    gider.delete()
                    return createErrorResponse(200, {"message": "Expense record is removed"})
                else:
                    return err_response
            else:
                return createErrorResponse(404, {"message": "Expense not found"})
        else:
            return createErrorResponse(400, {"message": "Expense not provided properly"})
            # bad request


