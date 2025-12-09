from django.contrib import admin
from django.urls import path


from .views import CreateUserView, VerifyAPIView, GetNewVerification, ChangeUserInformationView, ChangeUserPhotoView, \
    LoginView, LoginRefreshToken, LogoutView, ForgotPasswordView, ResetPasswordView

urlpatterns=[
    path('login/', LoginView.as_view(), name='login'),
    path('login/refresh/',LoginRefreshToken.as_view(), name='login_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('signup/',CreateUserView.as_view(),name='signup'),
    path('verify/',VerifyAPIView.as_view(),name='verify'),
    path('new-verify/',GetNewVerification.as_view(),name='new-verify'),
    path('change_user/',ChangeUserInformationView.as_view(),name='change-user'),
    path('change-user-photo/',ChangeUserPhotoView.as_view(),name='change-user-photo'),
    path('forgot_password/',ForgotPasswordView.as_view(),name='forgot_password'),
    path('reset_password/',ResetPasswordView.as_view(),name='reset_password'),


]