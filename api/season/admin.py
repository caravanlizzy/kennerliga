from django.contrib import admin

# Register your models here.
from season.models import Season


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    pass
