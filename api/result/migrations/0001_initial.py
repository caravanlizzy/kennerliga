# Generated by Django 4.2.1 on 2024-01-03 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField()),
                ('points', models.IntegerField()),
                ('league', models.IntegerField()),
                ('year', models.IntegerField()),
                ('starting_position', models.IntegerField(blank=True, null=True)),
                ('starting_points', models.IntegerField(blank=True, null=True)),
                ('league_points', models.IntegerField()),
                ('percentage_of_winner', models.FloatField(blank=True, null=True)),
                ('character', models.CharField(blank=True, max_length=144, null=True)),
                ('tie_breaker', models.CharField(blank=True, max_length=144, null=True)),
            ],
        ),
    ]