from django.contrib import admin, messages
from league.models import League, LeagueStanding, GameStanding
from services.standings_snapshot import rebuild_league_snapshot, rebuild_game_snapshot
from game.models import SelectedGame


from django.urls import path
from django.shortcuts import redirect
from django.utils.html import format_html
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.safestring import mark_safe

@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'season', 'level', 'status')
    list_filter = ('season', 'level', 'status', 'active_player')
    search_fields = ('season__year', 'season__month', 'level')
    raw_id_fields = ('season',)
    filter_horizontal = ('members',)
    actions = ['rebuild_all_standings']
    readonly_fields = ('recalculate_button', 'resolve_ties_button')

    def recalculate_button(self, obj):
        if not obj.id:
            return "-"
        return format_html(
            '<a class="button" href="{}">Rebuild Standings</a>',
            f"/admin/league/league/{obj.id}/rebuild/"
        )
    recalculate_button.short_description = "Recalculate"

    def resolve_ties_button(self, obj):
        if not obj.id:
            return "-"
        return format_html(
            '<a class="button" href="{}">Resolve Ties</a>',
            f"/admin/league/league/{obj.id}/resolve-ties/"
        )
    resolve_ties_button.short_description = "Resolve Ties"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:league_id>/rebuild/',
                self.admin_site.admin_view(self.rebuild_view),
                name='league-rebuild',
            ),
            path(
                '<int:league_id>/resolve-ties/',
                self.admin_site.admin_view(self.resolve_ties_view),
                name='league-resolve-ties',
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

    def _render_groups_index(self, request, league):
        groups = (
            LeagueStanding.objects
            .filter(league=league, unresolved_tie_group__isnull=False)
            .values_list('unresolved_tie_group', flat=True)
            .distinct()
        )
        if not groups:
            html = "<h2>No unresolved tie groups for this league.</h2>"
            return HttpResponse(mark_safe(html))

        lines = [
            f"<h2>Unresolved tie groups for {league}</h2>",
            "<ul>",
        ]
        for g in groups:
            url = f"/admin/league/league/{league.id}/resolve-ties/?group={g}"
            lines.append(f"<li><a href='{url}'>{g}</a></li>")
        lines.append("</ul>")
        return HttpResponse(mark_safe("\n".join(lines)))

    def _render_group_form(self, request, league, group_key: str):
        members = (
            LeagueStanding.objects
            .filter(league=league, unresolved_tie_group=group_key)
            .select_related('player_profile__user')
            .order_by('player_profile__profile_name')
        )
        if not members:
            # Might already be resolved; show info
            return HttpResponse(mark_safe(
                f"<p>Group <strong>{group_key}</strong> has no unresolved members. "
                f"It may have been resolved already.</p>"
                f"<p><a href='/admin/league/league/{league.id}/resolve-ties/'>Back</a></p>"
            ))

        # Default order by current name order
        default_order = ",".join(str(ls.player_profile_id) for ls in members)

        # Build a small HTML form
        reason_options = []
        from league.models import TieResolutionReason
        for val, label in list(TieResolutionReason.choices):
            reason_options.append(f"<option value='{val}'>{label}</option>")

        rows = [
            f"<li>{ls.player_profile.profile_name} (id={ls.player_profile_id})</li>" for ls in members
        ]

        # CSRF input
        from django.middleware.csrf import get_token
        csrf_input = f"<input type='hidden' name='csrfmiddlewaretoken' value='{get_token(request)}'>"

        html = f"""
        <h2>Resolve tie group {group_key} in {league}</h2>
        <p>Members in this group:</p>
        <ul>
            {''.join(rows)}
        </ul>
        <form method="post">
            {csrf_input}
            <input type="hidden" name="group_key" value="{group_key}">
            <p>
                <label>Reason:</label>
                <select name="reason" required>
                    {''.join(reason_options)}
                </select>
            </p>
            <p>
                <label>Note (optional):</label>
                <input type="text" name="note" style="width: 400px;" />
            </p>
            <p>
                <label>Player order (comma-separated PlayerProfile IDs, first is highest rank):</label><br>
                <input type="text" name="player_order" value="{default_order}" style="width: 400px;" />
            </p>
            <p>
                <button type="submit" class="button">Apply resolution</button>
                <a class="button" href="/admin/league/league/{league.id}/resolve-ties/">Cancel</a>
            </p>
        </form>
        """
        return HttpResponse(mark_safe(html))

    def resolve_ties_view(self, request, league_id):
        league = League.objects.get(id=league_id)
        group_key = request.GET.get('group')

        if request.method == 'GET':
            if group_key:
                return self._render_group_form(request, league, group_key)
            return self._render_groups_index(request, league)

        # POST: apply resolution
        group_key = request.POST.get('group_key')
        reason = request.POST.get('reason')
        note = request.POST.get('note')
        player_order_raw = request.POST.get('player_order', '')
        try:
            player_order = [int(x.strip()) for x in player_order_raw.split(',') if x.strip()]
        except ValueError:
            return HttpResponseBadRequest("Invalid player_order format; expected comma-separated integers.")

        # Basic validations mirroring API
        from league.models import LeagueTieResolution, LeagueTieResolutionEntry, TieResolutionReason
        if reason not in dict(TieResolutionReason.choices):
            return HttpResponseBadRequest("Invalid reason.")

        valid_ids = set(
            LeagueStanding.objects.filter(league=league, player_profile_id__in=player_order)
            .values_list('player_profile_id', flat=True)
        )
        if set(player_order) != valid_ids:
            return HttpResponseBadRequest("player_order must contain only PlayerProfile IDs present in this league standings.")

        # Optional: ensure group matches current unresolved groups unless already resolved
        current_groups = set(
            LeagueStanding.objects.filter(league=league, player_profile_id__in=player_order)
            .values_list('unresolved_tie_group', flat=True)
        )
        mismatched = [g for g in current_groups if g not in (None, group_key)]
        if mismatched:
            return HttpResponseBadRequest("Provided group_key does not match current standings groups.")

        # Upsert resolution
        resolution, _created = LeagueTieResolution.objects.update_or_create(
            league=league,
            group_key=group_key,
            defaults={'reason': reason, 'note': note, 'is_resolved': True}
        )

        # Replace entries with provided order
        resolution.entries.all().delete()
        LeagueTieResolutionEntry.objects.bulk_create([
            LeagueTieResolutionEntry(resolution=resolution, player_profile_id=pp_id, order_index=idx + 1)
            for idx, pp_id in enumerate(player_order)
        ])

        # Apply tie_break_priority and clear unresolved_tie_group
        standings = list(
            LeagueStanding.objects.filter(league=league, player_profile_id__in=player_order)
        )
        prio_base = len(player_order)
        prio_map = {pp_id: prio_base - idx for idx, pp_id in enumerate(player_order)}
        for ls in standings:
            ls.tie_break_priority = prio_map.get(ls.player_profile_id, 0)
            ls.unresolved_tie_group = None
        LeagueStanding.objects.bulk_update(standings, ["tie_break_priority", "unresolved_tie_group"])

        self.message_user(request, f"Resolved tie group {group_key}.", messages.SUCCESS)
        return redirect(f"/admin/league/league/{league_id}/change/")




@admin.register(LeagueStanding)
class LeagueStandingAdmin(admin.ModelAdmin):
    list_display = ('league', 'player_profile', 'wins', 'league_points', 'unresolved_tie_group', 'tie_break_priority', 'updated_at')
    list_filter = ('league', 'updated_at', 'unresolved_tie_group')
    search_fields = ('league__season__year', 'player_profile__profile_name')
    raw_id_fields = ('league', 'player_profile')
    ordering = ('-league_points', '-wins', '-tie_break_priority')
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


from league.models import LeagueTieResolution, LeagueTieResolutionEntry


@admin.register(LeagueTieResolution)
class LeagueTieResolutionAdmin(admin.ModelAdmin):
    list_display = ('league', 'group_key', 'reason', 'is_resolved', 'updated_at')
    list_filter = ('league', 'group_key', 'reason', 'is_resolved')
    search_fields = ('league__season__year',)
    raw_id_fields = ('league',)


@admin.register(LeagueTieResolutionEntry)
class LeagueTieResolutionEntryAdmin(admin.ModelAdmin):
    list_display = ('resolution', 'player_profile', 'order_index')
    list_filter = ('resolution__league',)
    search_fields = ('player_profile__profile_name',)
    raw_id_fields = ('resolution', 'player_profile')


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
