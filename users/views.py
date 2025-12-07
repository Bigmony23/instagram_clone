from django.utils import timezone
from enum import verify

from django.shortcuts import render
from pyexpat.errors import messages

from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, UpdateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from shared.utility import send_email, check_email_phone
from .models import User, DONE, CODE_VERIFIED, NEW, VIA_EMAIL, VIA_PHONE
from .serializers import SignupSerializer, ChangeUserInformation, ChangeUserPhotoSerializer, LoginSerializer, \
    LoginRefreshSerializer, LogoutSerializer, ForgotPasswordSerializer


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
        # print(verifies)

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

class GetNewVerification(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,request,*args,**kwargs):
        user=self.request.user
        self.check_verification(user)
        print(user.auth_type, user.email, user.phone)
        if user.auth_type==VIA_EMAIL:
            code=user.create_verify_code(VIA_EMAIL)
            send_email(user.email,code)
        elif user.auth_type==VIA_PHONE:
            code=user.create_verify_code(VIA_PHONE)
            email=user.email or f'{user.phone}@example.com'
            send_email(user.email,code)
        else:
            data={
                'message':'Email or phone is invalid'
            }
            raise ValidationError(data)
        send_email(email,code)
        return Response({
            'success':True,
            'message':'Your new verification code has been sent.'
        })



    @staticmethod
    def check_verification(user):
        verifies=user.verify_codes.filter(expiration_time__gte=timezone.now(),is_confirmed=False)

        if  verifies.exists():
            data={
                'message':'Your verification code is available '
            }
            raise ValidationError(data)

class ChangeUserInformationView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class=ChangeUserInformation
    http_method_names = ['patch','put']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'success':True,
                         'message':'User has been updated.',
                         'auth_status':instance.auth_status},status=status.HTTP_200_OK)
    def patch(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    def put(self, request, *args, **kwargs):
        kwargs['partial'] = False
        return self.update(request, *args, **kwargs)
        # super(ChangeUserInformationView, self).update(request, *args, **kwargs)
        # data={
        #     'success':True,
        #     'message':'User has been updated.',
        #     'auth_status':self.request.user.auth_status,
        # }
        # return Response(data,status=status.HTTP_200_OK)
    # def partial_update(self, request, *args, **kwargs):
    #     super(ChangeUserInformationView, self).update(request, *args, **kwargs)
    #     data={
    #         'success':True,
    #         'message':'User has been updated.',
    #         'auth_status':self.request.user.auth_status,
    #     }
    #     return Response(data,status=status.HTTP_200_OK)

class ChangeUserPhotoView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class=ChangeUserPhotoSerializer
    def put(self, request, *args, **kwargs):
        serializer = ChangeUserPhotoSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            serializer.update(user,serializer.validated_data)
            return Response({
                             'message':'User photo has been updated.',},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

class LoginRefreshToken(TokenRefreshView):
    serializer_class = LoginRefreshSerializer

class LogoutView(GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes=[IsAuthenticated]

    def post(self,request,*args,**kwargs):
        serializer_data=self.serializer_class(data=request.data)
        serializer_data.is_valid(raise_exception=True)
        try:
            refresh_token=self.request.data['refresh']
            token=RefreshToken(refresh_token)
            token.blacklist()
            data={'success':True,
                  'message':'Congratulations,You logged out successfully.',}
            return Response(data,status=205)
        except TokenError:
            return Response(status=409)
class ForgotPasswordView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ForgotPasswordSerializer

    def post(self,request,*args,**kwargs):
        serializer_data=self.serializer_class(data=request.data)
        serializer_data.is_valid(raise_exception=True)
        email_or_phone=serializer_data.validated_data.get('email_or_phone')
        user=serializer_data.validated_data.get('user')
        if check_email_phone(email_or_phone)=='phone':
            code=user.create_verify_code(VIA_PHONE)
            send_email(email_or_phone,code)
        elif check_email_phone(email_or_phone)=='email':
            code=user.create_verify_code(VIA_EMAIL)
            send_email(email_or_phone,code)
        return Response({
            'success':True,
            'message':'Verification code has been sent.',
            'access':user.token()['access_token'],
            'refresh':user.token()['refresh_token'],
            'user_status':user.auth_status,
        } ,status=200)



