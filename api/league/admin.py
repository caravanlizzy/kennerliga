from django.contrib import admin

# Register your models here.
from league.models import League

@admin.register(League)
class AuthorAdmin(admin.ModelAdmin):
    pass