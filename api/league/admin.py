from django.contrib import admin, messages
from league.models import League, LeagueStanding, GameStanding
from services.standings_snapshot import rebuild_league_snapshot, rebuild_game_snapshot
from game.models import SelectedGame


from django.urls import path
from django.shortcuts import redirect
from django.utils.html import format_html

@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'season', 'level', 'status')
    list_filter = ('season', 'level', 'status', 'active_player')
    search_fields = ('season__year', 'season__month', 'level')
    raw_id_fields = ('season',)
    filter_horizontal = ('members',)
    actions = ['rebuild_all_standings']
    readonly_fields = ('recalculate_button',)

    def recalculate_button(self, obj):
        if not obj.id:
            return "-"
        return format_html(
            '<a class="button" href="{}">Rebuild Standings</a>',
            f"/admin/league/league/{obj.id}/rebuild/"
        )
    recalculate_button.short_description = "Recalculate"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:league_id>/rebuild/',
                self.admin_site.admin_view(self.rebuild_view),
                name='league-rebuild',
            ),
        ]
        return custom_urls + urls

    def rebuild_view(self, request, league_id):
        league = League.objects.get(id=league_id)
        selected_games = SelectedGame.objects.filter(league=league)
        for sg in selected_games:
            rebuild_game_snapshot(sg)
        rebuild_league_snapshot(league)
        self.message_user(request, "Standings rebuilt successfully.", messages.SUCCESS)
        return redirect(f"/admin/league/league/{league_id}/change/")

    @admin.action(description="Rebuild all standings for selected leagues")
    def rebuild_all_standings(self, request, queryset):
        for league in queryset:
            selected_games = SelectedGame.objects.filter(league=league)
            for sg in selected_games:
                rebuild_game_snapshot(sg)
            rebuild_league_snapshot(league)
        self.message_user(request, f"Standings rebuilt for {queryset.count()} leagues.", messages.SUCCESS)




@admin.register(LeagueStanding)
class LeagueStandingAdmin(admin.ModelAdmin):
    list_display = ('league', 'player_profile', 'wins', 'league_points', 'updated_at')
    list_filter = ('league', 'updated_at')
    search_fields = ('league__season__year', 'player_profile__profile_name')
    raw_id_fields = ('league', 'player_profile')
    ordering = ('-league_points', '-wins')
    actions = ['rebuild_league_standings']
    readonly_fields = ('recalculate_button',)

    def recalculate_button(self, obj):
        if not obj.id:
            return "-"
        return format_html(
            '<a class="button" href="{}">Rebuild Overall Standings</a>',
            f"/admin/league/leaguestanding/{obj.id}/rebuild/"
        )
    recalculate_button.short_description = "Recalculate"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:ls_id>/rebuild/',
                self.admin_site.admin_view(self.rebuild_view),
                name='leaguestanding-rebuild',
            ),
        ]
        return custom_urls + urls

    def rebuild_view(self, request, ls_id):
        ls = LeagueStanding.objects.get(id=ls_id)
        rebuild_league_snapshot(ls.league)
        self.message_user(request, "Overall standings rebuilt successfully.", messages.SUCCESS)
        return redirect(f"/admin/league/leaguestanding/{ls_id}/change/")

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
    readonly_fields = ('recalculate_button',)

    def recalculate_button(self, obj):
        if not obj.id:
            return "-"
        return format_html(
            '<a class="button" href="{}">Rebuild Game Standings</a>',
            f"/admin/league/gamestanding/{obj.id}/rebuild/"
        )
    recalculate_button.short_description = "Recalculate"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:gs_id>/rebuild/',
                self.admin_site.admin_view(self.rebuild_view),
                name='gamestanding-rebuild',
            ),
        ]
        return custom_urls + urls

    def rebuild_view(self, request, gs_id):
        gs = GameStanding.objects.get(id=gs_id)
        rebuild_game_snapshot(gs.selected_game)
        rebuild_league_snapshot(gs.league)
        self.message_user(request, "Standings rebuilt successfully.", messages.SUCCESS)
        return redirect(f"/admin/league/gamestanding/{gs_id}/change/")

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
