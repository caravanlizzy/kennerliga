from django.contrib import admin, messages
from league.models import League, LeagueResult, LeagueStanding, GameStanding
from services.standings_snapshot import rebuild_league_snapshot, rebuild_game_snapshot
from game.models import SelectedGame


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'season', 'level', 'status')
    list_filter = ('season', 'level', 'status', 'active_player')
    search_fields = ('season__year', 'season__month', 'level')
    raw_id_fields = ('season',)
    filter_horizontal = ('members',)
    actions = ['rebuild_all_standings']

    @admin.action(description="Rebuild all standings for selected leagues")
    def rebuild_all_standings(self, request, queryset):
        for league in queryset:
            selected_games = SelectedGame.objects.filter(league=league)
            for sg in selected_games:
                rebuild_game_snapshot(sg)
            rebuild_league_snapshot(league)
        self.message_user(request, f"Standings rebuilt for {queryset.count()} leagues.", messages.SUCCESS)


@admin.register(LeagueResult)
class LeagueResultAdmin(admin.ModelAdmin):
    list_display = ('league', 'profile', 'league_points', 'position', 'last')
    list_filter = ('league', 'last')
    search_fields = ('league__season__year', 'profile__profile_name')
    raw_id_fields = ('league', 'profile')


@admin.register(LeagueStanding)
class LeagueStandingAdmin(admin.ModelAdmin):
    list_display = ('league', 'player_profile', 'wins', 'league_points', 'updated_at')
    list_filter = ('league', 'updated_at')
    search_fields = ('league__season__year', 'player_profile__profile_name')
    raw_id_fields = ('league', 'player_profile')
    ordering = ('-league_points', '-wins')
    actions = ['rebuild_league_standings']

    @admin.action(description="Rebuild overall standings for selected leagues")
    def rebuild_league_standings(self, request, queryset):
        leagues = set(queryset.values_list('league', flat=True))
        for league_id in leagues:
            league = League.objects.get(id=league_id)
            rebuild_league_snapshot(league)
        self.message_user(request, f"Overall standings rebuilt for {len(leagues)} leagues.", messages.SUCCESS)


@admin.register(GameStanding)
class GameStandingAdmin(admin.ModelAdmin):
    list_display = ('league', 'selected_game', 'player_profile', 'points', 'rank', 'league_points', 'updated_at')
    list_filter = ('league', 'updated_at')
    search_fields = ('league__season__year', 'player_profile__profile_name')
    raw_id_fields = ('league', 'selected_game', 'player_profile')
    ordering = ('-league_points', '-points')
    actions = ['rebuild_game_standings']

    @admin.action(description="Rebuild game and league standings for selected entries")
    def rebuild_game_standings(self, request, queryset):
        # We need to rebuild the whole game snapshot if even one entry is selected
        selected_games = set(queryset.values_list('selected_game', flat=True))
        leagues = set()
        for sg_id in selected_games:
            sg = SelectedGame.objects.get(id=sg_id)
            rebuild_game_snapshot(sg)
            leagues.add(sg.league)
        
        for league in leagues:
            rebuild_league_snapshot(league)
            
        self.message_user(request, f"Standings rebuilt for {len(selected_games)} games.", messages.SUCCESS)
