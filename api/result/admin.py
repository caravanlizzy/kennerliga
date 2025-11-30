from django.contrib import admin

from result.models import Result


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = (
        'player_profile',
        'get_selected_game',
        'league',
        'season',
        'points',
        'starting_position',
        'tie_breaker_resolved'
    )

    list_filter = (
        'league',
        'season',
        'tie_breaker_resolved'
    )

    search_fields = (
        'player_profile__profile_name',
        'selected_game__game__name'
    )

    readonly_fields = ('tie_breaker_resolved',)

    def get_selected_game(self, obj):
        return str(obj.selected_game)

    get_selected_game.short_description = 'Selected Game'
