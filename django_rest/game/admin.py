from django.contrib import admin
from nested_admin.nested import NestedModelAdmin, NestedStackedInline, NestedTabularInline

# Register your models here.
from game.models import Game, GameOption, GameOptionChoice


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
