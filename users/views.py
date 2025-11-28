from django.utils import timezone
from enum import verify

from django.shortcuts import render
from pyexpat.errors import messages

from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, DONE, CODE_VERIFIED, NEW
from .serializers import SignupSerializer

class CreateUserView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignupSerializer

# Create your views here.
class VerifyAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request,*args,**kwargs):
        user=self.request.user
        code=self.request.data.get('code')

        self.check_verify(user,code)
        return Response(
            data={
            'success':True,
            'auth_status':user.auth_status,
            'access':user.token()['access_token'],
            'refresh':user.token()['refresh_token'],
        })
    @staticmethod
    def check_verify(user,code):
        verifies=user.verify_codes.filter(expiration_time__gte=timezone.now(),code=code,is_confirmed=False)
        print(verifies)

        if not verifies.exists():
            data={
                'message':'Your verification code is invalid'
            }
            raise ValidationError(data)
        verifies.update(is_confirmed=True)
        if user.auth_status ==NEW:
            user.auth_status=CODE_VERIFIED
            user.save()
        return True

