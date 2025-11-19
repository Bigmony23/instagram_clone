from django.contrib import admin
from django.urls import path


from .views import CreateUserView

urlpatterns=[
    path('admin/', admin.site.urls),
    path('signup/',CreateUserView.as_view(),name='signup'),
]