from django.contrib import admin
from django.urls import path


from .views import CreateUserView, VerifyAPIView, GetNewVerification

urlpatterns=[

    path('signup/',CreateUserView.as_view(),name='signup'),
    path('verify/',VerifyAPIView.as_view(),name='verify'),
    path('new-verify/',GetNewVerification.as_view(),name='new-verify'),
]