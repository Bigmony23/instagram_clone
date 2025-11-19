from .models import User,UserConfirmation,VIA_PHONE,VIA_EMAIL,CODE_VERIFIED,DONE,NEW,PHOTO_STEP
from rest_framework import exceptions
from django.db.models import Q
from rest_framework import serializers
from shared.utility import check_email_phone
from rest_framework.exceptions import ValidationError

class SignupSerializer(serializers.ModelSerializer):
    id =serializers.UUIDField(read_only=True)
    def __init__(self,*args,**kwargs):
        super(SignupSerializer,self).__init__(*args,**kwargs)
        self.fields['email_phone_number']=serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('id','auth_type','auth_status')
        extra_kwargs = {
            'auth_type':{'read_only':True,'required':False},
            'auth_status':{'read_only':True,'required':False},
        }
    def validate(self,data):
        super(SignupSerializer,self).validate(data)
        data=self.auth_validate(data)
        return data
    @staticmethod
    def auth_validate(data):
        user_input=str(data.get('email_phone_number')).lower()
        #tekshirish
        input_type=check_email_phone(user_input)
        print('user_input',user_input)
        print('input_type',input_type)
        return data


        # user_input=




