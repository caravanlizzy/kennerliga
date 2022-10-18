from django.contrib import admin

# Register your models here.
from game.models import Game, GameOption, GameOptionCategory


@admin.register(Game)
class AuthorAdmin(admin.ModelAdmin):
    pass


@admin.register(GameOptionCategory)
class AuthorAdmin(admin.ModelAdmin):
    pass


@admin.register(GameOption)
class AuthorAdmin(admin.ModelAdmin):
    pass
