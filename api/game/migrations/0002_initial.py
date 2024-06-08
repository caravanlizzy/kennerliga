# Generated by Django 5.0.4 on 2024-06-08 11:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("game", "0001_initial"),
        ("league", "0001_initial"),
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="platform",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="user.platform"
            ),
        ),
        migrations.AddField(
            model_name="faction",
            name="game",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="game.game"
            ),
        ),
        migrations.AddField(
            model_name="gameoption",
            name="game",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="options",
                to="game.game",
            ),
        ),
        migrations.AddField(
            model_name="gameoption",
            name="only_if_option",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="only_if_options",
                to="game.gameoption",
            ),
        ),
        migrations.AddField(
            model_name="gameoptionchoice",
            name="option",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="choices",
                to="game.gameoption",
            ),
        ),
        migrations.AddField(
            model_name="gameoption",
            name="only_if_choice",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="only_if_options",
                to="game.gameoptionchoice",
            ),
        ),
        migrations.AddField(
            model_name="resultconfig",
            name="game",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="game.game"
            ),
        ),
        migrations.AddField(
            model_name="selectedgame",
            name="game",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="selected_games",
                to="game.game",
            ),
        ),
        migrations.AddField(
            model_name="selectedgame",
            name="league",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="selected_games",
                to="league.league",
            ),
        ),
        migrations.AddField(
            model_name="selectedgame",
            name="player",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="selected_games",
                to="user.platformplayer",
            ),
        ),
        migrations.AddField(
            model_name="selectedoption",
            name="choice",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="selections",
                to="game.gameoptionchoice",
            ),
        ),
        migrations.AddField(
            model_name="selectedoption",
            name="game_option",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="selections",
                to="game.gameoption",
            ),
        ),
        migrations.AddField(
            model_name="selectedoption",
            name="selected_game",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="selected_options",
                to="game.selectedgame",
            ),
        ),
        migrations.AddField(
            model_name="resultconfig",
            name="starting_points_system",
            field=models.ForeignKey(
                default=1,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="game.startingpointsystem",
            ),
        ),
        migrations.AddField(
            model_name="tiebreaker",
            name="result_config",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="game.resultconfig"
            ),
        ),
    ]
