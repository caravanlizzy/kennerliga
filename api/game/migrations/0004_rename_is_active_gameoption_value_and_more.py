# Generated by Django 5.0.2 on 2024-03-17 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_rename_enabled_gameoption_is_active_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gameoption',
            old_name='is_active',
            new_name='value',
        ),
        migrations.RemoveField(
            model_name='gameoption',
            name='active_inactive_option',
        ),
        migrations.AddField(
            model_name='gameoptionchoice',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]