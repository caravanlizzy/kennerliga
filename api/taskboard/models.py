from django.db import models


class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = "Low"
        MEDIUM = "Medium"
        HIGH = "High"

    class Status(models.TextChoices):
        TODO = "To Do"
        IN_PROGRESS = "In Progress"
        DONE = "Done"
        DECLINED = "Declined"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")

    priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.MEDIUM
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.TODO
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-id"]

    def __str__(self) -> str:
        return f"[{self.status}] {self.title}"
