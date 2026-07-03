import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("game", "0018_populate_winconditions"),
    ]

    operations = [
        # Now that every TieBreaker has a win_condition, enforce non-null.
        migrations.AlterField(
            model_name="tiebreaker",
            name="win_condition",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tie_breakers",
                to="game.wincondition",
            ),
        ),
        # Drop the legacy direct link to ResultConfig.
        migrations.RemoveField(
            model_name="tiebreaker",
            name="result_config",
        ),
    ]
