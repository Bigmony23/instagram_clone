from django.contrib import admin
from django.urls import path


from .views import CreateUserView, VerifyAPIView, GetNewVerification, ChangeUserInformationView, ChangeUserPhotoView

urlpatterns=[

    path('signup/',CreateUserView.as_view(),name='signup'),
    path('verify/',VerifyAPIView.as_view(),name='verify'),
    path('new-verify/',GetNewVerification.as_view(),name='new-verify'),
    path('change_user/',ChangeUserInformationView.as_view(),name='change-user'),
    path('change-user-photo/',ChangeUserPhotoView.as_view(),name='change-user-photo'),
]