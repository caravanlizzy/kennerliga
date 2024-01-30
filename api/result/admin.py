from django.contrib import admin

# Register your models here.
from result.models import Result


@admin.register(Result)
class AuthorAdmin(admin.ModelAdmin):
    pass
