# Generated by Django 5.0.2 on 2024-03-16 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_rename_value_gameoption_enabled'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gameoption',
            old_name='enabled',
            new_name='is_active',
        ),
        migrations.RemoveField(
            model_name='gameoptionchoice',
            name='is_active',
        ),
        migrations.AddField(
            model_name='gameoption',
            name='active_inactive_option',
            field=models.BooleanField(default=True),
        ),
    ]