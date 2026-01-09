from django.contrib import admin, messages
from nested_admin.nested import NestedModelAdmin, NestedStackedInline, NestedTabularInline

# Register your models here.
from game.models import Game, GameOption, GameOptionChoice, StartingPointSystem, Faction, TieBreaker, \
    ResultConfig, SelectedGame, BanDecision, SelectedOption, GameOptionAvailabilityCondition, \
    GameOptionAvailabilityGroup
from services.standings_snapshot import rebuild_game_snapshot, rebuild_league_snapshot


# @admin.register(GameOption)
# class Options(admin.ModelAdmin):
#     pass


class ChoicesAdmin(NestedTabularInline):
    model = GameOptionChoice
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "option":
            # Attempt to find the Game ID from the URL (e.g., /admin/game/game/5/change/)
            resolved = request.resolver_match
            if resolved and 'object_id' in resolved.kwargs:
                game_id = resolved.kwargs['object_id']
                kwargs["queryset"] = GameOption.objects.filter(game_id=game_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class AvailabilityConditionInline(NestedTabularInline):
    model = GameOptionAvailabilityCondition
    extra = 0
    fk_name = 'group'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        resolved = request.resolver_match
        game_id = resolved.kwargs.get('object_id') if resolved else None

        if game_id:
            if db_field.name == "option":
                kwargs["queryset"] = GameOption.objects.filter(game_id=game_id)
            elif db_field.name == "choice":
                kwargs["queryset"] = GameOptionChoice.objects.filter(option__game_id=game_id)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class AvailabilityGroupInline(NestedStackedInline):
    model = GameOptionAvailabilityGroup
    extra = 0
    inlines = (AvailabilityConditionInline,)


class OptionsAdmin(NestedStackedInline):
    model = GameOption
    extra = 0
    inlines = (ChoicesAdmin, AvailabilityGroupInline)
    # Exclude legacy fields from the nested view to keep it clean
    exclude = ('only_if_option', 'only_if_choice', 'only_if_value')


@admin.register(Game)
class GameAdmin(NestedModelAdmin):
    list_display = ('name', 'platform')
    list_filter = ('platform',)
    search_fields = ('name',)
    inlines = (OptionsAdmin,)


@admin.register(StartingPointSystem)
class StartingPointSystemAdmin(admin.ModelAdmin):
    list_display = ('code', 'description')
    list_filter = ('code',)  # Allows filtering by the 'code' field on the right side of the list page
    search_fields = ('code', 'description')
    ordering = ('code',)  # Orders the entries in the admin list by 'code'
    fields = ('code', 'description')  # Defines fields to be editable in the detail view


@admin.register(Faction)
class FactionAdmin(admin.ModelAdmin):
    list_display = ('name', 'game', 'level')
    list_filter = ('game', 'level')
    search_fields = ('name',)


@admin.register(TieBreaker)
class TieBreakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'result_config', 'order')
    list_filter = ('result_config__game',)


@admin.register(ResultConfig)
class ResultConfigAdmin(admin.ModelAdmin):
    list_display = ('game', 'is_asymmetric', 'has_starting_player_order', 'starting_points_system', 'has_points')
    list_filter = ('game',)


from django.urls import path
from django.shortcuts import redirect
from django.utils.html import format_html

@admin.register(SelectedGame)
class SelectedGameAdmin(admin.ModelAdmin):
    list_display = ('profile', 'game', 'league')
    list_filter = ('league', 'game', 'profile')
    search_fields = ('profile__profile_name', 'game__name')
    actions = ['rebuild_selected_game_standings']
    readonly_fields = ('recalculate_button',)

    def recalculate_button(self, obj):
        if not obj.id:
            return "-"
        return format_html(
            '<a class="button" href="{}">Rebuild Standings</a>',
            f"/admin/game/selectedgame/{obj.id}/rebuild/"
        )
    recalculate_button.short_description = "Recalculate"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:sg_id>/rebuild/',
                self.admin_site.admin_view(self.rebuild_view),
                name='selectedgame-rebuild',
            ),
        ]
        return custom_urls + urls

    def rebuild_view(self, request, sg_id):
        sg = SelectedGame.objects.get(id=sg_id)
        rebuild_game_snapshot(sg)
        rebuild_league_snapshot(sg.league)
        self.message_user(request, "Standings rebuilt successfully.", messages.SUCCESS)
        return redirect(f"/admin/game/selectedgame/{sg_id}/change/")

    @admin.action(description="Rebuild standings for selected games")
    def rebuild_selected_game_standings(self, request, queryset):
        leagues = set()
        for sg in queryset:
            rebuild_game_snapshot(sg)
            leagues.add(sg.league)
        
        for league in leagues:
            rebuild_league_snapshot(league)
            
        self.message_user(request, f"Standings rebuilt for {queryset.count()} games.", messages.SUCCESS)


@admin.register(BanDecision)
class BanDecisionAdmin(admin.ModelAdmin):
    list_display = ('player_banning', 'league', 'selected_game', 'created_at')
    list_filter = ('league', 'player_banning')
    date_hierarchy = 'created_at'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "selected_game":
            # Check if we are editing an existing object
            obj_id = request.resolver_match.kwargs.get('object_id')
            if obj_id:
                ban_decision = self.get_object(request, obj_id)
                if ban_decision and ban_decision.league:
                    kwargs["queryset"] = SelectedGame.objects.filter(league=ban_decision.league)
            else:
                # If it's a new object, you can check for league_id in GET params
                # (useful if navigating from a link like /admin/.../add/?league=1)
                league_id = request.GET.get('league')
                if league_id:
                    kwargs["queryset"] = SelectedGame.objects.filter(league_id=league_id)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(SelectedOption)
class SelectedOptionAdmin(admin.ModelAdmin):
    list_display = ('selected_game', 'game_option', 'choice', 'value')
    list_filter = ('selected_game__game', 'game_option')
