from django.contrib import admin

# Register your models here.
from game.models import Game, GameSettingsOptionChoice, GameSettingsCategory


@admin.register(Game)
class AuthorAdmin(admin.ModelAdmin):
    pass


@admin.register(GameSettingsCategory)
class AuthorAdmin(admin.ModelAdmin):
    pass


@admin.register(GameSettingsOptionChoice)
class AuthorAdmin(admin.ModelAdmin):
    pass
