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
from rest_framework import serializers, exceptions
from django.contrib.auth import get_user_model
from shared.utility import check_email_phone, send_email
from users.models import VIA_EMAIL, VIA_PHONE, NEW

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
            send_email(user.phone, code) # for now
            # send_phone_code(user.phone, code)
        user.save()
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update(instance.token())
        return data

