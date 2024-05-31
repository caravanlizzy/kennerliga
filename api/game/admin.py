from django.contrib import admin
from nested_admin.nested import NestedModelAdmin, NestedStackedInline, NestedTabularInline

# Register your models here.
from game.models import Game, GameOption, GameOptionChoice, StartingPointSystem, Platform, Faction, TieBreaker


# @admin.register(GameOption)
# class Options(admin.ModelAdmin):
#     pass


class ChoicesAdmin(NestedTabularInline):
    model = GameOptionChoice
    extra = 0


class OptionsAdmin(NestedStackedInline):
    model = GameOption
    extra = 0
    inlines = (ChoicesAdmin,)


@admin.register(Game)
class GameAdmin(NestedModelAdmin):
    inlines = (OptionsAdmin,)


@admin.register(StartingPointSystem)
class StartingPointSystemAdmin(admin.ModelAdmin):
    list_display = ('code', 'description')
    list_filter = ('code',)  # Allows filtering by the 'code' field on the right side of the list page
    search_fields = ('code', 'description')
    ordering = ('code',)  # Orders the entries in the admin list by 'code'
    fields = ('code', 'description')  # Defines fields to be editable in the detail view


@admin.register(Platform)
class Platform(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Faction)
class Faction(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(TieBreaker)
class TieBreaker(admin.ModelAdmin):
    list_display = ('name',)
