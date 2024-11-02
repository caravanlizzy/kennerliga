# Generated by Django 5.1.1 on 2024-11-01 15:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0006_leagueresult_last_leagueresult_position_and_more'),
        ('season', '0003_alter_season_participants'),
    ]

    operations = [
        migrations.AlterField(
            model_name='league',
            name='season',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='season', to='season.season'),
        ),
    ]
