from django.contrib import admin
from django.contrib.auth.management.commands.changepassword import UserModel

from .models import User,UserConfirmation

class UserAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'email','phone')

admin.site.register(User, UserAdmin)
admin.site.register(UserConfirmation)


# Register your models here.
