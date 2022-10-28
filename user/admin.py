from django.contrib import admin

# Register your models here.
from user.models import User


@admin.register(User)
class AuthorAdmin(admin.ModelAdmin):
    fields = ('username', 'email', 'password')
