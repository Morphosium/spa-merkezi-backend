from rest_framework.response import Response
from rest_framework.request import Request

def createErrorResponse(errorCode : int, object : dict) -> Response:
    return Response(object, status=errorCode)