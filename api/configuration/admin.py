from django.contrib import admin

from configuration.models import AppConfiguration


@admin.register(AppConfiguration)
class AppConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "max_same_game_per_year",
        "tie_decider_game",
        "created_by",
        "created_at",
    )
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)
