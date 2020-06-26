import traceback

from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView 
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny

from utils.errorResponse import createErrorResponse
from .serializers import UserSerializer
from utils.SubeIliskileri import iliskiVarMi, iliskiliSubeler
from cinarspa_models.models import SubeTemsilcisi
# Create your views here.



class loggedUserInformation(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if (request.user is not None):
            userSerializer = UserSerializer(request.user)
            return Response(userSerializer.data)

class createUser(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            subeId = request.data["subeId"] if "subeId" in request.data else -1
            if subeId == -1:
                return createErrorResponse(404, {"message": "Branch not found"})
            else:
                if iliskiVarMi(request.user, subeId) is False:
                    return createErrorResponse(404, {"message": "Branch not found"})

            if request.user.is_staff:
                kul_id = request.user.id
                stFilter = SubeTemsilcisi.objects.filter(sube__id=subeId, kullanici__id=kul_id)[0]
            elif request.user.is_superuser:
                stFilter = SubeTemsilcisi.objects.filter(sube__id=subeId)[0]

            serialized = UserSerializer(data=request.data)

            # subeAuthorized = iliskiliSubeler(request.user)
            if subeId > -1 and iliskiVarMi(request.user, subeId):
                if serialized.is_valid():
                    createdUser = User.objects.create_user(
                        email=request.data['email'],
                        username=request.data['username'],
                        password=request.data['password'],
                        is_staff=True
                    )
                    createdUser.save()
                    yeniSubeIliskisi = SubeTemsilcisi(
                        sube=stFilter.sube,
                        kullanici=createdUser
                    )
                    yeniSubeIliskisi.save()
                    return Response(serialized.data, status=status.HTTP_201_CREATED)
                else:
                    return createErrorResponse(404, serialized.errors)
            else:
                return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exception:
            traceback.print_exc()
            return createErrorResponse(500, {"error": str(exception.__class__)})

