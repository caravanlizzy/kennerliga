# Generated by Django 5.2 on 2025-05-21 13:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_rename_game_bandecision_banned_game'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bandecision',
            old_name='banned_game',
            new_name='game',
        ),
    ]
