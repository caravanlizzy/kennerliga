# Generated by Django 5.0.6 on 2024-08-30 13:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0003_alter_league_members'),
        ('user', '0002_rename_player_platformplayer_player_profile_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='active_player',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.playerprofile'),
        ),
    ]
