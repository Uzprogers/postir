from django.contrib import admin

from apps.models import User


# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
