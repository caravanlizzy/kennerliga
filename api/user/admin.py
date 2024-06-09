from django.contrib import admin

# Register your models here.
from user.models import User, Platform

admin.site.register(User)


@admin.register(Platform)
class Platform(admin.ModelAdmin):
    list_display = ('name',)
