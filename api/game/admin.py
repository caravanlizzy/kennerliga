from django.contrib import admin
from nested_admin.nested import NestedModelAdmin, NestedStackedInline, NestedTabularInline

# Register your models here.
from game.models import Game, GameOption, GameOptionChoice, StartingPointSystem, Faction, TieBreaker, \
    ResultConfig, SelectedGame, BanDecision, SelectedOption, GameOptionAvailabilityCondition, \
    GameOptionAvailabilityGroup


# @admin.register(GameOption)
# class Options(admin.ModelAdmin):
#     pass


class ChoicesAdmin(NestedTabularInline):
    model = GameOptionChoice
    extra = 0


class AvailabilityConditionInline(NestedTabularInline):
    model = GameOptionAvailabilityCondition
    extra = 0
    fk_name = 'group'


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
    list_display = ('name', 'game')
    list_filter = ('game',)
    search_fields = ('name',)


@admin.register(TieBreaker)
class TieBreakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'result_config', 'order')
    list_filter = ('result_config__game',)


@admin.register(ResultConfig)
class ResultConfigAdmin(admin.ModelAdmin):
    list_display = ('game', 'is_asymmetric', 'has_starting_player_order', 'starting_points_system', 'has_points')
    list_filter = ('game',)


@admin.register(SelectedGame)
class SelectedGameAdmin(admin.ModelAdmin):
    list_display = ('profile', 'game', 'league')
    list_filter = ('league', 'game', 'profile')
    search_fields = ('profile__profile_name', 'game__name')


@admin.register(BanDecision)
class BanDecisionAdmin(admin.ModelAdmin):
    list_display = ('player_banning', 'league', 'selected_game', 'created_at')
    list_filter = ('league', 'player_banning')
    date_hierarchy = 'created_at'


@admin.register(SelectedOption)
class SelectedOptionAdmin(admin.ModelAdmin):
    list_display = ('selected_game', 'game_option', 'choice', 'value')
    list_filter = ('selected_game__game', 'game_option')
