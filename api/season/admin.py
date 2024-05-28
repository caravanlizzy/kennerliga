from django.contrib import admin

# Register your models here.
from season.models import Season


@admin.register(Season)
class AuthorAdmin(admin.ModelAdmin):
    pass
