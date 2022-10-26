from django.contrib import admin

# Register your models here.
from game.models import Game, GameSettingsOption, GameSettingsCategory


@admin.register(Game)
class AuthorAdmin(admin.ModelAdmin):
    pass


@admin.register(GameSettingsCategory)
class AuthorAdmin(admin.ModelAdmin):
    pass


@admin.register(GameSettingsOption)
class AuthorAdmin(admin.ModelAdmin):
    pass
