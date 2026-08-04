from django.contrib import admin

from announcement.models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "visible_from", "visible_until", "is_visible")
    list_filter = ("type", "visible_from", "visible_until")
    search_fields = ("title", "content")
    date_hierarchy = "visible_from"
    ordering = ("-visible_from",)

    def is_visible(self, obj):
        from django.utils import timezone
        now = timezone.now()
        return obj.visible_from <= now <= obj.visible_until
    is_visible.boolean = True
    is_visible.short_description = "Active Now"
