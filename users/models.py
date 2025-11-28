import uuid
from datetime import datetime, timedelta
import random

from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from unicodedata import normalize
from django.utils import timezone
from shared.models import BaseModel


ORDINARY_USER,MANAGER,ADMIN=("ordinary_user","manager","admin")
VIA_EMAIL,VIA_PHONE=("via_email","via_phone")
NEW,CODE_VERIFIED,DONE,PHOTO_STEP=("new","code_verified","done","photo_step")

class User(AbstractUser,BaseModel):
    USER_ROLES = (
        (ORDINARY_USER,ORDINARY_USER ),
        (MANAGER,MANAGER),
        (ADMIN,ADMIN)
    )
    AUTH_TYPE_CHOICES = (
        (VIA_EMAIL,VIA_EMAIL ),
        (VIA_PHONE,VIA_PHONE )
    )
    AUTH_STATUS_CHOICES = (
        (NEW,NEW),
        (CODE_VERIFIED,CODE_VERIFIED),
        (DONE,DONE),
        (PHOTO_STEP,PHOTO_STEP)
    )
    user_roles=models.CharField(max_length=31, choices=USER_ROLES,default=ORDINARY_USER)
    auth_type=models.CharField(max_length=31,choices=AUTH_TYPE_CHOICES)
    auth_status=models.CharField(max_length=31,choices=AUTH_STATUS_CHOICES,default=NEW)
    email=models.EmailField(unique=True,blank=True,null=True)
    phone=models.CharField(max_length=13,unique=True,null=True,blank=True)
    photo=models.ImageField(upload_to='user_photos/',null=True,blank=True,validators=[FileExtensionValidator(allowed_extensions=['jpg','jpeg','png','heic','heif'])])
    # created_time=
    # updated_time=
    # id=
    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def create_verify_code(self,verify_type):
        code="".join([str(random.randint(0,100) %10) for _ in range(4)])
        UserConfirmation.objects.create(
            user_id=self.id,
            verify_type=verify_type,
            code=code,)
        return code
    def check_username(self):
        if not self.username or self.username.strip() == "":
            temp_username=f'instagram_{uuid.uuid4().__str__().split("-")[-1]}'
            while User.objects.filter(username=temp_username):
                temp_username=f'{temp_username}{random.randint(0,9)}'
            self.username=temp_username
    def check_email(self):
        if  self.email:
            normalize_email=self.email.lower()
            self.email=normalize_email

    def check_password_auth(self):
        if  not self.password:
            temp_password=f'password_{uuid.uuid4().__str__().split("-")[-1]}'
            self.password=temp_password
    def hashing_password(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)

    def token(self):
        refresh=RefreshToken.for_user(self)
        return {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }
    def clean(self):
        if self.email:
            self.email=self.email.lower()
        if self.username and self.username.strip() == "":
            self.username=self.username.strip()
        return super().clean()


    def save(self, *args, **kwargs):
        self.check_email()
        if not self.username or self.username.strip() == "":
            self.check_username()

        self.check_password_auth()

        self.hashing_password()
        super(User,self).save(*args, **kwargs)




PHONE_EXPIRE=2
EMAIL_EXPIRE=5
class UserConfirmation(BaseModel):
    TYPE_CHOICES = ((VIA_EMAIL, VIA_EMAIL), (VIA_PHONE, VIA_PHONE))
    code=models.CharField(max_length=9)
    verify_type=models.CharField(max_length=31,choices=TYPE_CHOICES)
    user=models.ForeignKey('users.User',related_name='verify_codes',on_delete=models.CASCADE)
    expiration_time=models.DateTimeField(null=True)
    is_confirmed=models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.__str__())
    def save(self, *args, **kwargs):
        if self.verify_type==VIA_EMAIL:
            self.expiration_time=timezone.now()+timedelta(minutes=EMAIL_EXPIRE)
        else:
            self.expiration_time=timezone.now()+timedelta(minutes=PHONE_EXPIRE)
        super(UserConfirmation,self).save(*args, **kwargs)


# Create your models here.
