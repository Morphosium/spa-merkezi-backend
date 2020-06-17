from django.shortcuts import render
from rest_framework.views import APIView 
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserSerializer
# Create your views here.



class loggedUserInformation(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if (request.user is not None):
            userSerializer = UserSerializer(request.user)
            return Response(userSerializer.data)