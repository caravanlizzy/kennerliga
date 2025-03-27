# Generated by Django 5.1.7 on 2025-03-27 12:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('league', '0001_initial'),
        ('season', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='active_player',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='season.seasonparticipant'),
        ),
        migrations.AddField(
            model_name='league',
            name='members',
            field=models.ManyToManyField(related_name='leagues_member', to='season.seasonparticipant'),
        ),
        migrations.AddField(
            model_name='league',
            name='season',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='season', to='season.season'),
        ),
        migrations.AddField(
            model_name='leagueresult',
            name='league',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='league.league'),
        ),
    ]
