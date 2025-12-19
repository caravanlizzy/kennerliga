from django.contrib import admin
from result.models import Result


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = (
        'player_profile',
        'get_selected_game',
        'get_factions',
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

    # Optimizes Foreign Key lookups in the list view (prevents N+1 queries)
    list_select_related = (
        'player_profile',
        'league',
        'season',
        'selected_game',
        'selected_game__game'
    )

    def get_queryset(self, request):
        """
        Optimizes Many-to-Many lookups for the factions list.
        """
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('factions')

    def get_selected_game(self, obj):
        return str(obj.selected_game)

    get_selected_game.short_description = 'Selected Game'

    def get_factions(self, obj):
        return ", ".join([f.name for f in obj.factions.all()])

    get_factions.short_description = 'Factions'