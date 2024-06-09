from django.contrib import admin

# Register your models here.
from user.models import User, Platform, PlatformPlayer, PlayerProfile

admin.site.register(User)


@admin.register(PlayerProfile)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('profile_name', 'user', 'get_platforms')

    def get_platforms(self, obj):
        return ", ".join([pp.platform.name for pp in PlatformPlayer.objects.filter(player=obj)])

    get_platforms.short_description = 'Platforms'


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(PlatformPlayer)  # Assuming the model name you referred to as PlatformPlayer is actually PlatformPlayer
class PlatformPlayerAdmin(admin.ModelAdmin):
    list_display = ('player', 'platform', 'name')
