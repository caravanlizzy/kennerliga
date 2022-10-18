from django.contrib import admin

# Register your models here.
from match_result.models import MatchResult


@admin.register(MatchResult)
class AuthorAdmin(admin.ModelAdmin):
    pass
