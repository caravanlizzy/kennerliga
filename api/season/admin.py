from django.contrib import admin

# Register your models here.
from season.models import Season

from django.contrib import admin
from season.models import Season, SeasonParticipant


class SeasonParticipantInline(admin.TabularInline):
    model = SeasonParticipant
    extra = 0
    fields = ('profile', 'rank')


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'month', 'status', 'season_start_time')
    list_filter = ('status', 'year')
    search_fields = ('year', 'month')
    ordering = ('-year', '-month')

    inlines = [SeasonParticipantInline]

    fieldsets = (
        (None, {
            'fields': ('year', 'month')
        }),
        ('Status', {
            'fields': ('status',),
            'classes': ('wide',)
        })
    )
