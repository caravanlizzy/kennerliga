from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PushDevice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token", models.CharField(db_index=True, max_length=300, unique=True)),
                (
                    "platform",
                    models.CharField(
                        choices=[
                            ("android", "Android"),
                            ("ios", "iOS"),
                            ("web", "Web"),
                            ("unknown", "Unknown"),
                        ],
                        default="unknown",
                        max_length=20,
                    ),
                ),
                ("device_id", models.CharField(blank=True, db_index=True, max_length=120, null=True)),
                ("app_version", models.CharField(blank=True, max_length=40, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("notify_registration_open", models.BooleanField(default=True)),
                ("notify_league_started", models.BooleanField(default=True)),
                ("notify_active_player", models.BooleanField(default=True)),
                ("last_seen_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="push_devices",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "indexes": [models.Index(fields=["user", "is_active"], name="user_pushdev_user_id_24b6a0_idx")],
            },
        ),
    ]
