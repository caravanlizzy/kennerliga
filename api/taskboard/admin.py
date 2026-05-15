from django.contrib import admin

from taskboard.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "priority", "status", "updated_at")
    list_filter = ("status", "priority")
    search_fields = ("title", "description")
    ordering = ("-updated_at",)
