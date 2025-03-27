# Generated by Django 5.1.7 on 2025-03-27 12:24

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('month', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)], verbose_name='month in the current year')),
                ('status', models.CharField(choices=[('Nächste', 'Next'), ('Anmeldung offen', 'Open'), ('Laufend', 'Running'), ('Beendet', 'Done')], default='Nächste', max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='SeasonParticipant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'ordering': ['rank'],
            },
        ),
    ]
