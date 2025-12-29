from django.contrib import admin
from league.models import League, LeagueResult, LeagueStanding, GameStanding


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'season', 'level', 'status')
    list_filter = ('season', 'level', 'status', 'active_player')
    search_fields = ('season__year', 'season__month', 'level')
    raw_id_fields = ('season',)
    filter_horizontal = ('members',)


@admin.register(LeagueResult)
class LeagueResultAdmin(admin.ModelAdmin):
    list_display = ('league', 'profile', 'league_points', 'position', 'last')
    list_filter = ('league', 'last')
    search_fields = ('league__season__year', 'profile__profile_name')
    raw_id_fields = ('league', 'profile')


@admin.register(LeagueStanding)
class LeagueStandingAdmin(admin.ModelAdmin):
    list_display = ('league', 'player_profile', 'points', 'wins', 'league_points', 'updated_at')
    list_filter = ('league', 'updated_at')
    search_fields = ('league__season__year', 'player_profile__profile_name')
    raw_id_fields = ('league', 'player_profile')
    ordering = ('-league_points', '-wins', '-points')


@admin.register(GameStanding)
class GameStandingAdmin(admin.ModelAdmin):
    list_display = ('league', 'selected_game', 'player_profile', 'points', 'rank', 'league_points', 'updated_at')
    list_filter = ('league', 'updated_at')
    search_fields = ('league__season__year', 'player_profile__profile_name')
    raw_id_fields = ('league', 'selected_game', 'player_profile')
    ordering = ('-league_points', '-points')
