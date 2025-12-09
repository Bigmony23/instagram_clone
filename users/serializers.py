#
# from rest_framework import exceptions
# from django.db.models import Q
# from rest_framework import serializers
# from shared.utility import check_email_phone
# from rest_framework.exceptions import ValidationError
# from shared.utility import send_email
# from users.models import User, VIA_EMAIL, VIA_PHONE
#
#
# class SignupSerializer(serializers.ModelSerializer):
#     id =serializers.UUIDField(read_only=True)
#     def __init__(self,*args,**kwargs):
#         super(SignupSerializer,self).__init__(*args,**kwargs)
#         self.fields['email_phone_number']=serializers.CharField(required=False)
#
#     class Meta:
#         model = User
#         fields = ('id','auth_type','auth_status')
#         extra_kwargs = {
#             'auth_type':{'read_only':True,'required':False},
#             'auth_status':{'read_only':True,'required':False},
#         }
#
#     def create(self, validated_data):
#         validated_data.pop('email_phone_number', None)
#         user = User.objects.create(**validated_data)
#         print(user)
#         #email code
#         #if phone phone code
#         if user.auth_type==VIA_EMAIL:
#             code=user.create_verify_code(VIA_EMAIL)
#             print(code)
#             send_email(user.email,code)
#         elif user.auth_type==VIA_PHONE:
#             code=user.create_verify_code(VIA_PHONE)
#             # print(code)
#             # send_phone_code(user.phone,code)
#         user.save()
#         return user
#
#     def validate(self, data):
#         data = super().validate(data) or {}
#
#         # получить вручную
#         data["email_phone_number"] = self.initial_data.get("email_phone_number")
#
#         auth_data = self.auth_validate(data)
#         data.update(auth_data)
#         return data
#
#     @staticmethod
#     def auth_validate(data):
#         user_input=str(data.get('email_phone_number')).lower()
#         #tekshirish
#         input_type=check_email_phone(user_input)
#         if input_type=='email':
#             data={
#                 'email':user_input,
#                 'auth_type':VIA_EMAIL,
#             }
#         elif input_type=='phone':
#             data={'phone':user_input,
#                   "auth_type":VIA_PHONE,}
#         else:
#             data={
#                 'success': False,
#                 'message':"You must send phone number or email.",
#             }
#             raise exceptions.ValidationError(data)
#         # print(data)
#         return data
#
#     def validate_email_phone_number(self, value):
#         value = value.lower()
#         if value and User.objects.filter(email=value).exists():
#             data={
#                 'success': False,
#                 'message':"Email already exists.",
#
#             }
#             raise exceptions.ValidationError(data)
#         elif value and User.objects.filter(phone=value).exists():
#             data={
#                 'success': False,
#                 'message':"Phone number already exists.",
#             }
#             raise exceptions.ValidationError(data)
#         return value
#
#     def to_representation(self, instance):
#         data = super(SignupSerializer, self).to_representation(instance)
#         data.update(instance.token())
#
#
#         # user_input=
#
#
#
#
# users/serializers.py
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import serializers, exceptions
from django.contrib.auth import get_user_model, authenticate
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenObtainSerializer, \
    TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken

from shared.utility import check_email_phone, send_email, check_user_type
from users.models import VIA_EMAIL, VIA_PHONE, NEW, CODE_VERIFIED, DONE, PHOTO_DONE

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    email_phone_number = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'auth_type', 'auth_status', 'email_phone_number')
        read_only_fields = ('auth_type', 'auth_status', 'email', 'phone')

    def validate(self, attrs):
        # attrs is dict-like
        user_input = attrs.get('email_phone_number', '').strip().lower()
        input_type = check_email_phone(user_input)

        if input_type == 'email':
            attrs['email'] = user_input
            attrs['auth_type'] = VIA_EMAIL
        else:
            attrs['phone'] = user_input
            attrs['auth_type'] = VIA_PHONE

        attrs['auth_status'] = NEW
        return attrs

    def create(self, validated_data):
        # remove helper field
        validated_data.pop('email_phone_number', None)

        # build fields for User.create
        user_data = {}
        if validated_data.get('email'):
            user_data['email'] = validated_data.get('email')
            user_data['username'] = validated_data.get('email')  # username fallback
        else:
            user_data['phone'] = validated_data.get('phone')
            user_data['username'] = validated_data.get('phone')

        user_data['auth_type'] = validated_data.get('auth_type')
        user_data['auth_status'] = validated_data.get('auth_status', NEW)

        user = User.objects.create(**user_data)

        # create and send code
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            email = user.email or f'{user.phone}@example.com'
            send_email(email, code) # for now
            # send_phone_code(user.phone, code)
        user.save()
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update(instance.token())
        return data

class ChangeUserInformation(serializers.Serializer):

    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    username=serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    # class Meta:
    #     model = User
    #     fields = ['first_name', 'last_name', 'username', 'password', 'confirm_password']
    #     extra_kwargs = {
    #         'first_name': {'required': False},
    #         'last_name': {'required': False},
    #         'username': {'required': False},
    #     }

    def validate(self, data):
        if not getattr(self,'partial', False):
            required_fields = ['first_name', 'last_name', 'username', 'password', 'confirm_password']
            missing=[f for f in required_fields if f not in self.initial_data]
            if missing:
                raise exceptions.ValidationError({field:'This field is required.' for field in missing})
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        if password != confirm_password:
            raise exceptions.ValidationError({'message': 'Passwords do not match'})
        if password:
            validate_password(password)
            validate_password(confirm_password)
        return data
    def validate_username(self, value):
        if len(value) < 5 or len(value) > 30:
            raise  ValidationError({'message': 'Username must be between 5 and 30 characters'})
        if value.isdigit():
            raise ValidationError({'message': 'Username must not contain only numbers'})
        return value
    def validate_first_name(self, value):
        if len(value) < 5 or len(value) > 30:
            raise ValidationError({'message': 'First name must be between 5 and 30 characters'})
        if value.isdigit():
            raise ValidationError({'message': 'First name must not contain only numbers'})
        return value
    def validate_last_name(self, value):
        if len(value)<5 or len(value)>30:
            raise ValidationError({'message': 'Last name must be between 5 and 30 characters'})
        if value.isdigit():
            raise ValidationError({'message': 'Last name must not contain only numbers'})
        return value
    def update(self, instance, validated_data):

        # # Обновляем только то, что пришло
        # for field, value in validated_data.items():
        #     if field == 'password':
        #         instance.set_password(value)
        #     elif field != 'confirm_password':
        #         setattr(instance, field, value)
        # if validated_data.get('password'):
        #     instance.set_password(validated_data.get('password'))
        # if instance.auth_status == CODE_VERIFIED:
        #     instance.auth_status=DONE
        # instance.save()
        # return instance
        for attr in ('first_name', 'last_name', 'username'):
            if attr in validated_data:
                setattr(instance, attr, validated_data[attr])
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        if getattr(instance,'auth_status',None)=='code_verified':
            instance.auth_status = DONE

        instance.save()
        return instance

class ChangeUserPhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField(validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg','heic','heif'])])

    def update(self, instance, validated_data):
        photo = validated_data.get('photo')
        if photo:
            instance.photo=photo
            instance.auth_status = PHOTO_DONE
            instance.save()
        return instance


class LoginSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super(LoginSerializer,self).__init__(*args, **kwargs)
        self.fields['userinput']=serializers.CharField(required=True)
        self.fields['username']=serializers.CharField(required=False, read_only=True)

    def auth_validate(self,attrs):
        user_input = attrs.get('userinput')#email or phone number or username
        if check_user_type(user_input)=='username':
            username=user_input
        elif check_user_type(user_input)=='email':
            user=self.get_user(email__iexact=user_input)
            username=user.username
        elif check_user_type(user_input)=='phone':
            user=self.get_user(phone=user_input)
            username=user.username
        else:
            data={
                'success': True,
                'message':'You should send email,username or phone to login'

            }
            raise ValidationError(data)
        authentication_kwargs = {
            self.username_field: username,
            'password': attrs.get('password'),
        }
        current_user=User.objects.filter(username__iexact=username).first()

        if current_user is not None and current_user.auth_status in [NEW,CODE_VERIFIED]:
            raise ValidationError({'succes':False,
                'message':'You are not fully registered uet'})
        user=authenticate(**authentication_kwargs)
        if user is not None:
            self.user=user
        else:
            raise ValidationError({'success':False,'message':'Invalid credentials'})
    def validate(self,attrs):
        self.auth_validate(attrs)
        if self.user.auth_status not in [DONE,PHOTO_DONE]:
            raise PermissionDenied({'You can not login you don not have permissions'})
        data=self.user.token()
        data['auth_status']=self.user.auth_status
        data['full_name']=self.user.full_name

        return data

    def get_user(self,**kwargs):
        users=User.objects.filter(**kwargs)
        if not users.exists():
            raise ValidationError({'message':'User not found'})
        else:
            return users.first()

class LoginRefreshSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        data=super().validate(attrs)
        access_token_instance=AccessToken(data['access'])
        user_id=access_token_instance['user_id']
        user=get_object_or_404(User,id=user_id)
        update_last_login(None,user)
        return data

class LogoutSerializer(serializers.Serializer):
    refresh=serializers.CharField()

class ForgotPasswordSerializer(serializers.Serializer):
    email_or_phone=serializers.CharField(write_only=True,required=True)

    def validate(self,attrs):
        email_or_phone=attrs.get('email_or_phone',None)
        if email_or_phone is None:
            raise ValidationError({'success':False,'message':'Please enter valid phone number'})
        user=User.objects.filter(Q(phone=email_or_phone) | Q(email=email_or_phone))
        if not user.exists():
            raise NotFound({'detail':'User not found'})
        attrs['user']=user.first()
        return attrs


class ResetPasswordSerializer(serializers.ModelSerializer):
    id =serializers.UUIDField(read_only=True)
    password = serializers.CharField(write_only=True,required=True,max_length=8)
    confirm_password = serializers.CharField(write_only=True,required=True,max_length=8)

    class Meta:
        model = User
        fields = ('id','password','confirm_password')

    def validate(self,attrs):
        password=attrs.get('password')
        confirm_password=attrs.get('confirm_password')
        if password != confirm_password:
            raise ValidationError({'success':False,'message':'Passwords do not match'})
        if password:
            validate_password(password)
        return attrs
    def update(self,instance,validated_data):
        password=validated_data.pop('password')
        instance.set_password(password)
        return super(ResetPasswordSerializer,self).update(instance,validated_data)








