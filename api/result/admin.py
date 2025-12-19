from django.contrib import admin
from result.models import Result
from game.models import Faction


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

    # Hide the legacy single faction field and use a better UI for Many-to-Many
    exclude = ('faction',)
    filter_horizontal = ('factions',)

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

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Filters the factions available in the dropdown to only show
        those belonging to the game associated with this result.
        """
        if db_field.name == "factions":
            # Get the result object ID from the URL if we are in the change form
            obj_id = request.resolver_match.kwargs.get('object_id')
            if obj_id:
                try:
                    result = Result.objects.get(id=obj_id)
                    kwargs["queryset"] = Faction.objects.filter(game=result.selected_game.game)
                except Result.DoesNotExist:
                    pass
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_selected_game(self, obj):
        return str(obj.selected_game)

    get_selected_game.short_description = 'Selected Game'

    def get_factions(self, obj):
        return ", ".join([f.name for f in obj.factions.all()])

    get_factions.short_description = 'Factions'