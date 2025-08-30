from django.contrib import admin

# Register your models here.
from result.models import Result


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('player_profile', 'get_selected_game', 'league',)

    def get_selected_game(self, obj):
        return str(obj.selected_game)

    get_selected_game.short_description = 'Selected Game'
