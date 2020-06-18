from django.shortcuts import render
from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from utils.arrayUtils import containsInDictionaryKey
from utils.errorResponse import createErrorResponse
# Create your views here.

class createAppointment(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        data : dict = request.data
        if (containsInDictionaryKey(data,["isimSoyisim","hizmetTipi","subeId","tarih"])):
            return Response(data)
        else:
            return createErrorResponse(400,{"message":"1 field or more than 1 fields are missing"}) #
