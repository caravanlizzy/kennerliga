# Generated manually to support adding WinCondition without data loss.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("game", "0016_game_related_games"),
    ]

    operations = [
        migrations.CreateModel(
            name="WinCondition",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "condition_type",
                    models.CharField(
                        choices=[("POINTS", "Points"), ("OPTION", "Option")],
                        default="OPTION",
                        max_length=20,
                    ),
                ),
                ("order", models.PositiveIntegerField(default=0)),
                (
                    "result_config",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="win_conditions",
                        to="game.resultconfig",
                    ),
                ),
            ],
            options={
                "ordering": ["order", "name"],
            },
        ),
        migrations.CreateModel(
            name="WinConditionOption",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("order", models.PositiveIntegerField(default=0)),
                (
                    "win_condition",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="options",
                        to="game.wincondition",
                    ),
                ),
            ],
            options={
                "ordering": ["order", "name"],
            },
        ),
        # Add the new FK as NULLABLE first so existing rows can be migrated.
        migrations.AddField(
            model_name="tiebreaker",
            name="win_condition",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tie_breakers",
                to="game.wincondition",
            ),
        ),
    ]
