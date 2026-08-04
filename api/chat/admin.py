from django.contrib import admin

from chat.models import Chat


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ("text_preview", "user", "datetime", "label")
    list_filter = ("datetime", "label", "user")
    search_fields = ("text", "user__username", "label")
    date_hierarchy = "datetime"
    ordering = ("-datetime",)

    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_preview.short_description = "Message"
