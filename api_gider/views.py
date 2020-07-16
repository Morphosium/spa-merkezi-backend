from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from dateutil.parser import parse

from api_gider.serializers import EkstraGiderSerializer
from cinarspa_models.models import EkstraGider
from utils.ExtraExpenses import extra_expenses
from utils.SubeIliskileri import iliskiVarMi
from utils.errorResponse import createErrorResponse
from utils.pagination import pagination


def _generic_control(request) -> (bool, Response):
    """Controls is branch provided and is user any privaliges
    Return 1: when controlling if has a issue, return false. Else then, it is true
    Return 2: If has issue, response will be returned. But there is no issue, nothing returned"""
    date_ = request.query_params["date"]
    sube_: str = request.query_params["sube_id"]
    date = parse(date_)
    if sube_.isnumeric():
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
    authentication_classes = [IsAuthenticated]

    def get(self, request: Request):

        flag, errorResponse = _generic_control(request)
        if flag:
            date_ = request.query_params["date"]
            sube = int(request.query_params["sube_id"])
            expenses = extra_expenses(request.user, sube)
            paginated_expenses = pagination(expenses, request.query_params.get("page"),
                                            request.query_params.get("size"))
            return createErrorResponse(200, paginated_expenses)
        else:
            return errorResponse

class AddExpense(APIView):
    authentication_classes = [IsAuthenticated]

    def post(self, request):
        flag, error_response = _generic_control(request)
        if flag:
            parsedThing = EkstraGiderSerializer(source=request.data)
            if parsedThing.is_valid():
                yeniGider = EkstraGider(**request.data)
                yeniGider.save()
                return createErrorResponse(201, {"message": "Expense created successfully",
                                                 "object": EkstraGiderSerializer(yeniGider).data}
                                           )
            else:
                return createErrorResponse(400, {"errors": parsedThing.errors, "message": "Required fields are missing"})
        else:
            return error_response
