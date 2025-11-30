from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from user.models import User, Platform, PlatformPlayer, PlayerProfile, UserInviteLink, Feedback


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'is_staff', 'is_active', 'date_joined', 'last_login')
    search_fields = ('username',)
    ordering = ('-date_joined',)
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ('profile_name', 'user', 'get_platforms')
    search_fields = ('profile_name', 'user__username')
    list_select_related = ('user',)
    raw_id_fields = ('user',)

    def get_platforms(self, obj):
        return ", ".join([pp.platform.name for pp in obj.platform_links.select_related('platform')])

    get_platforms.short_description = 'Platforms'


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_players_count')
    search_fields = ('name',)

    def get_players_count(self, obj):
        return obj.player_links.count()

    get_players_count.short_description = 'Number of Players'


@admin.register(PlatformPlayer)
class PlatformPlayerAdmin(admin.ModelAdmin):
    list_display = ('player_profile', 'platform', 'name')
    list_select_related = ('player_profile', 'platform')
    search_fields = ('name', 'player_profile__profile_name', 'platform__name')
    list_filter = ('platform',)


@admin.register(UserInviteLink)
class UserInviteLinkAdmin(admin.ModelAdmin):
    list_display = ('label', 'created_by', 'created_at', 'expires_at', 'is_expired')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('label', 'created_by__username')
    readonly_fields = ('key_hash', 'created_at')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'datetime', 'truncated_message')
    list_filter = ('datetime',)
    search_fields = ('message', 'user__username')
    readonly_fields = ('datetime',)

    def truncated_message(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message

    truncated_message.short_description = 'Message'
